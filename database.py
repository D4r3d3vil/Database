from typing import Dict, List, Callable, Union

class Field:
    """Represents a field in a database table."""
    def __init__(self, name: str, data_type: type):
        self.name = name
        self.data_type = data_type

class Row:
    """Represents a row in a database table."""
    def __init__(self, **kwargs: Union[str, int, float, bool]):
        self.fields: Dict[str, Union[str, int, float, bool]] = {}
        for field_name, field_value in kwargs.items():
            self.fields[field_name] = field_value

    def add_field(self, field_name: str, field_value: Union[str, int, float, bool]):
        """Adds a field to the row."""
        self.fields[field_name] = field_value

class TableNotFoundError(Exception):
    """Exception raised when a table is not found in the database."""
    pass

class Table:
    """Represents a database table."""
    def __init__(self, name: str):
        self.name = name
        self._fields: List[Field] = []
        self._rows: List[Row] = []
        self._related_tables: Dict[str, Table] = {}

    def add_fields(self, fields_dict: Dict[str, type]):
        """Adds multiple fields to the table."""
        for field_name, data_type in fields_dict.items():
            self.add_field(field_name, data_type)

    def add_field(self, field_name: str, data_type: type):
        """Adds a field to the table."""
        self._fields.append(Field(field_name, data_type))

    def add_row(self, **kwargs: Union[str, int, float, bool]):
        """Adds a row to the table."""
        if len(kwargs) != len(self._fields):
            raise ValueError("Number of fields in row does not match the number of fields in table schema.")

        for field_name, field_value in kwargs.items():
            expected_data_type = next((field.data_type for field in self._fields if field.name == field_name), None)
            if expected_data_type is None:
                raise ValueError(f"Field '{field_name}' does not exist in table schema.")
            if not isinstance(field_value, expected_data_type):
                raise ValueError(f"Field '{field_name}' type does not match the expected type.")

        row = Row(**kwargs)
        self._rows.append(row)

    def find(self, condition: Callable[[Row], bool]) -> Union[Row, None]:
        """Finds a single row in the table based on a condition."""
        for row in self._rows:
            if condition(row):
                return row
        return None
    
    def findMany(self, condition: Callable[[Row], bool], amount: int = 0) -> List[Row]:
        """Finds multiple rows in the table based on a condition."""
        rowsFound = []
        for row in self._rows:
            if condition(row):
                rowsFound.append(row)
                if len(rowsFound) == amount:
                    return rowsFound
        return rowsFound
    
    @property
    def fields(self) -> List[str]:
        """Returns a list of field names in the table."""
        return [field.name for field in self._fields]

    @property
    def rows(self) -> List[Dict[str, Union[str, int, float, bool]]]:
        """Returns a list of rows in the table."""
        return [row.fields for row in self._rows]

class Database:
    """Represents a database."""
    def __init__(self):
        self._tables: Dict[str, Table] = {}

    def create(self, table_name: str) -> Table:
        """Creates a new table in the database."""
        table = Table(table_name)
        self._tables[table_name] = table
        return table

    def get(self, table_name: str) -> Table:
        """Gets a table from the database."""
        if table_name in self._tables:
            return self._tables[table_name]
        else:
            raise TableNotFoundError(f"Table '{table_name}' does not exist.")