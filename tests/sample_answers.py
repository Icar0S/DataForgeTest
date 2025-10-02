"""Sample answers for testing DSL generation and code generation."""

SAMPLE_ANSWERS = {
    # General
    "What is the name of the dataset you want to validate?": "customer_data",
    ("What is the source of the data "
     "(e.g., a file path, a database table)?"): "/path/to/customer_data.csv",
    "What is the format of the data (e.g., CSV, JSON, Parquet)?": "CSV",

    # Schema Validation
    "Does the data have a header?": "yes",
    ("What are the expected column names, in order?"): (
        "id, first_name, last_name, email, registration_date, age, "
        "country_code, start_date, end_date"),
    ("What is the expected data type for each column "
     "(e.g., string, integer, float, date)?"): (
        "integer, string, string, string, date, integer, string, date, date"),

    # Data Integrity
    ("Which columns should not contain any missing values "
     "(i.e., are mandatory)?"): "id, email",
    ("Which columns should contain unique values "
     "(i.e., are primary keys)?"): "id, email",
    ("Are there any columns that should have a specific format "
     "(e.g., a date format like YYYY-MM-DD)?"): (
        "registration_date:YYYY-MM-DD, start_date:YYYY-MM-DD, "
        "end_date:YYYY-MM-DD"),

    # Value Constraints
    ("Are there any columns that should have a minimum or "
     "maximum value?"): "age:18:99",
    ("Are there any columns that should only contain values from a "
     "specific set (e.g., a list of categories)?"): "country_code:['US','CA','MX']",
    ("Are there any columns that should match a specific regular "
     "expression pattern?"): r"email:^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    ("Are there any columns for which you want to check the value "
     "distribution (e.g., to ensure certain values appear with a "
     "specific frequency)?"): "country_code:US:0.4:0.6, country_code:CA:0.1:0.3",

    # Cross-Column Validation
    ("Are there any relationships between two columns that should always "
     "hold true (e.g., 'start_date' must be before 'end_date', 'price' "
     "must be greater than 'cost')? List as 'column1:operator:column2', "
     "separated by commas. Supported operators: <, <=, >, >=, ==, !=. "
     "(e.g., start_date:<:end_date, price:>:cost)"): (
        "start_date:<:end_date, price:>:cost")
}

SAMPLE_ANSWERS_WITH_ERRORS = {
    # General (no errors expected here)
    "What is the name of the dataset you want to validate?": "error_data",
    ("What is the source of the data "
     "(e.g., a file path, a database table)?"): "/path/to/error_data.csv",
    "What is the format of the data (e.g., CSV, JSON, Parquet)?": "CSV",

    # Schema Validation (mismatched counts)
    "Does the data have a header?": "yes",
    "What are the expected column names, in order?": "id, name",
    # Too many types
    ("What is the expected data type for each column "
     "(e.g., string, integer, float, date)?"): (
        "integer, string, string, float, date"),

    # Data Integrity (invalid format for formatted columns)
    ("Which columns should not contain any missing values "
     "(i.e., are mandatory)?"): "id",
    ("Which columns should contain unique values "
     "(i.e., are primary keys)?"): "id",
    # Missing format
    ("Are there any columns that should have a specific format "
     "(e.g., a date format like YYYY-MM-DD)?"): (
        "registration_date:YYYY-MM-DD, invalid_col"),

    # Value Constraints (invalid range, invalid set, invalid regex)
    # Invalid number, missing max
    ("Are there any columns that should have a minimum or "
     "maximum value?"): "age:invalid_num:99, price:10:",
    # Missing closing bracket
    ("Are there any columns that should only contain values from a "
     "specific set (e.g., a list of categories)?"): (
        "status:[active,inactive, invalid_set"),
    # Missing pattern for phone
    ("Are there any columns that should match a specific regular "
     "expression pattern?"): (
        r"email:^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$, "
        "phone:123-456-7890"),

    # Cross-Column Validation (invalid operator)
    ("Are there any relationships between two columns that should always "
     "hold true (e.g., 'start_date' must be before 'end_date', 'price' "
     "must be greater than 'cost')? List as 'column1:operator:column2', "
     "separated by commas. Supported operators: <, <=, >, >=, ==, !=. "
     "(e.g., start_date:<:end_date, price:>:cost)"): "col_a:invalid_op:col_b"
}
