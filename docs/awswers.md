HAPPY_PATH_ANSWERS = {
    2     "What is the name of the dataset you want to
      validate? (e.g., customer_data)":
      "my_sales_data",
    3     "What is the source of the data (e.g., a
      file path like /data/customer.csv, or a database
      table name like sales.customers)?":
      "/data/sales.csv",
    4     "What is the format of the data (e.g., CSV,
      JSON, Parquet, Delta)?": "CSV",
    5
    6     "Does the data have a header? (yes/no)":
      "yes",
    7     "What are the expected column names, in
      order? (e.g., id, first_name, last_name, email)"
      : "order_id, product_name, quantity, price,
      order_date, customer_id",
    8     "What is the expected data type for each
      column (e.g., integer, string, float, date)?
      Please list them in the same order as column
      names, separated by commas. (e.g., integer,
      string, string, string)": "integer, string,
      integer, float, date, string",
    9
   10     "Which columns should not contain any
      missing values (i.e., are mandatory)? List them
      separated by commas. (e.g., id, email)":
      "order_id, product_name, quantity, price,
      order_date",
   11     "Which columns should contain unique values
      (i.e., are primary keys)? List them separated by
      commas. (e.g., id, order_id)": "order_id",
   12     "Are there any columns that should have a
      specific format (e.g., a date format like
      YYYY-MM-DD)? List as 'column:format', separated
      by commas. (e.g., registration_date:YYYY-MM-DD,
      transaction_time:HH:mm:ss)":
      "order_date:YYYY-MM-DD",
   13
   14     "Are there any columns that should have a
      minimum or maximum value? List as
      'column:min:max', 'column::max', or
      'column:min:', separated by commas. (e.g.,
      age:18:99, price::1000, quantity:1:)":
      "quantity:1:100, price:0.01:",
   15     "Are there any columns that should only
      contain values from a specific set (e.g., a list
      of categories)? List as
      'column:[value1,value2]', separated by '],'.
      (e.g., status:[active,inactive,pending],
      gender:[M,F,Other])":
      "product_name:[Laptop,Mouse,Keyboard,Monitor]",
   16     "Are there any columns that should match a
      specific regular expression pattern? List as
      'column:pattern', separated by commas. (e.g.,
      email:^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-
      Z]{2,}$$, phone_number:^\\d{3}-\\d{3}-\\d{4}$)":
      "customer_id:^CUST-\\d{5}$",
   17     "Are there any columns for which you want to
      check the value distribution (e.g., to ensure
      certain values appear with a specific
      frequency)? List as
      'column:value:min_freq:max_freq', separated by
      commas. (e.g., status:active:0.7:1.0,
      status:inactive:0.0:0.1)":
      "product_name:Laptop:0.3:0.5",
   18
   19     "Are there any relationships between two
      columns that should always hold true (e.g.,
      'start_date' must be before 'end_date', 'price'
      must be greater than 'cost')? List as
      'column1:operator:column2', separated by commas.
      Supported operators: <, <=, >, >=, ==, !=.
      (e.g., start_date:<:end_date, price:>:cost)":
      "quantity:<:100, price:>:0"
   20 }