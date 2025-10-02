# PySpark imports are used in the generated code strings
# These imports are not directly used in the generator function
# but are included in the generated code output


def generate_pyspark_code(dsl):
    """Generates PySpark code from the DSL."""
    dataset_name = dsl.get("dataset", {}).get("name", "data")
    source_path = dsl.get("dataset", {}).get("source", "")
    data_format = dsl.get("dataset", {}).get("format", "").lower()
    has_header = dsl.get("dataset", {}).get("has_header", False)

    code = f"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, to_date, regexp_extract, array_contains, countDistinct

spark = SparkSession.builder \
    .appName("DataQualityValidation_{dataset_name}") \
    .getOrCreate()

all_failed_records = [] # To collect all failed records for summary

print("Reading data from {source_path} (format: {data_format})")
try:
    if "csv" == "{data_format}":
        df = spark.read.format("csv")\
            .option("header", "{str(has_header).lower()}")\
            .option("inferSchema", "true")\
            .load("{source_path}")
    elif "json" == "{data_format}":
        df = spark.read.json("{source_path}")
    elif "parquet" == "{data_format}":
        df = spark.read.parquet("{source_path}")
    elif "delta" == "{data_format}":
        df = spark.read.format("delta").load("{source_path}")
    else:
        print(f"Unsupported data format: {data_format}. Please load data manually.")
        spark.stop()
        exit(1)
except Exception as e:
    print(f"Error reading data: {{e}}")
    spark.stop()
    exit(1)

print("Data loaded successfully. Total records: {{df.count()}}")
df.printSchema()

# Apply data quality rules
print("\n--- Applying Data Quality Rules ---")
"""

    for rule in dsl.get("rules", []):
        rule_type = rule.get("type")
        column = rule.get("column")
        columns = rule.get("columns")  # For uniqueness rule

        if rule_type == "not_null":
            code += f"""
print(f"Checking not_null for column: {column}")
failed_not_null = df.filter(col("{column}").isNull())
failed_count = failed_not_null.count()
if failed_count > 0:
    print(f"  FAIL: {{failed_count}} records have nulls in column '{column}'.")
    print("    Sample failed records:")
    failed_not_null.limit(5).show(truncate=False)
    all_failed_records.append((f"not_null_{column}", failed_count))
else:
    print(f"  PASS: Column '{column}' has no nulls.")
"""
        elif rule_type == "uniqueness":
            cols_str = ", ".join([f"'{c}'" for c in columns])
            code += f"""
print(f"Checking uniqueness for columns: {cols_str}")
failed_uniqueness = df.groupBy({cols_str}).count().filter(col("count") > 1)
failed_count = failed_uniqueness.count()
if failed_count > 0:
    print(f"  FAIL: {{failed_count}} unique combinations found with duplicates in columns {cols_str}.")
    print("    Sample failed records:")
    failed_uniqueness.limit(5).show(truncate=False)
    all_failed_records.append((f"uniqueness_{'_'.join(columns)}", failed_count))
else:
    print(f"  PASS: Columns {cols_str} have unique values.")
"""
        elif rule_type == "format":
            fmt = rule.get("format")
            # More robust date format validation
            date_formats = {
                "YYYY-MM-DD": "yyyy-MM-dd",
                "MM-DD-YYYY": "MM-dd-yyyy",
                "DD/MM/YYYY": "dd/MM/yyyy",
                "YYYY/MM/DD": "yyyy/MM/dd",
            }
            spark_date_format = date_formats.get(fmt.upper())

            if spark_date_format:
                code += f"""
print(f"Checking date format '{fmt}' for column: {column}")
failed_format = df.filter(to_date(col("{column}"), "{spark_date_format}").isNull() & col("{column}").isNotNull())
failed_count = failed_format.count()
if failed_count > 0:
    print(f"  FAIL: {{failed_count}} records have invalid date format in column '{column}'.")
    print("    Sample failed records:")
    failed_format.limit(5).show(truncate=False)
    all_failed_records.append((f"format_{column}", failed_count))
else:
    print(f"  PASS: Column '{column}' has valid date format.")
"""
            else:  # Generic format check using regex (if a regex pattern is provided in the format string)
                # This assumes the 'format' answer could be a regex directly if not a known date format
                code += f"""
print(f"Checking custom format (regex) '{fmt}' for column: {column}")
failed_format = df.filter(~col("{column}").rlike("{fmt}"))
failed_count = failed_format.count()
if failed_count > 0:
    print(f"  FAIL: {{failed_count}} records do not match the custom format (regex) in column '{column}'.")
    failed_format.limit(5).show(truncate=False)
    all_failed_records.append((f"format_{column}", failed_count))
else:
    print(f"  PASS: Column '{column}' values match the custom format (regex).")
"""
        elif rule_type == "range":
            min_val = rule.get("min")
            max_val = rule.get("max")
            range_condition = []
            if min_val is not None:
                range_condition.append(f'col("{column}") < {min_val}')
            if max_val is not None:
                range_condition.append(f'col("{column}") > {max_val}')

            if range_condition:
                condition_str = " | ".join(range_condition)
                code += f"""
print(f"Checking range [{min_val if min_val is not None else '-inf'}, {max_val if max_val is not None else 'inf'}] for column: {column}")
failed_range = df.filter({condition_str})
failed_count = failed_range.count()
if failed_count > 0:
    print(f"  FAIL: {{failed_count}} records are outside the expected range in column '{column}'.")
    print("    Sample failed records:")
    failed_range.limit(5).show(truncate=False)
    all_failed_records.append((f"range_{column}", failed_count))
else:
    print(f"  PASS: Column '{column}' values are within the expected range.")
"""
        elif rule_type == "in_set":
            values = rule.get("values", [])
            values_str = ", ".join([f"'{v}'" for v in values])
            code += f"""
print(f"Checking values in set [{values_str}] for column: {column}")
failed_in_set = df.filter(~col("{column}").isin({values_str}))
failed_count = failed_in_set.count()
if failed_count > 0:
    print(f"  FAIL: {{failed_count}} records have values not in the expected set in column '{column}'.")
    print("    Sample failed records:")
    failed_in_set.limit(5).show(truncate=False)
    all_failed_records.append((f"in_set_{column}", failed_count))
else:
    print(f"  PASS: Column '{column}' values are within the expected set.")
"""
        elif rule_type == "regex":
            pattern = rule.get("pattern")
            code += f"""
print(f"Checking regex pattern '{pattern}' for column: {column}")
failed_regex = df.filter(~col("{column}").rlike("{pattern}"))
failed_count = failed_regex.count()
if failed_count > 0:
    print(f"  FAIL: {{failed_count}} records do not match the regex pattern in column '{column}'.")
    print("    Sample failed records:")
    failed_regex.limit(5).show(truncate=False)
    all_failed_records.append((f"regex_{column}", failed_count))
else:
    print(f"  PASS: Column '{column}' values match the regex pattern.")
"""
        elif rule_type == "value_distribution":
            value = rule.get("value")
            min_freq = rule.get("min_freq")
            max_freq = rule.get("max_freq")
            code += f"""
print(f"Checking value distribution for column '{column}' (value: '{value}', min_freq: {min_freq}, max_freq: {max_freq})")
total_count = df.count()
value_count = df.filter(col("{column}") == "{value}").count()
    if total_count > 0:
        actual_freq = value_count / total_count
        if {min_freq} <= actual_freq <= {max_freq}:
            print(f"  PASS: Value '{value}' in column '{column}' has frequency {{actual_freq:.4f}}, which is within [{min_freq}, {max_freq}].")
        else:
            print(f"  FAIL: Value '{value}' in column '{column}' has frequency {{actual_freq:.4f}}, which is outside [{min_freq}, {max_freq}].")
            all_failed_records.append((f"value_distribution_{column}_{value}", actual_freq))
    else:
        print(f"  WARNING: Dataset is empty, cannot check value distribution for column '{column}'.")
"""
        elif rule_type == "cross_column_comparison":
            col1 = rule.get("column1")
            operator = rule.get("operator")
            col2 = rule.get("column2")

            code += f"""
print(f"Checking cross-column comparison: {col1} {operator} {col2}")
failed_comparison = df.filter(~(col("{col1}") {operator} col("{col2}")))
failed_count = failed_comparison.count()
if failed_count > 0:
    print(f"  FAIL: {{failed_count}} records where '{col1}' {operator} '{col2}' is false.")
    print("    Sample failed records:")
    failed_comparison.limit(5).show(truncate=False)
    all_failed_records.append((f"cross_column_comparison_{col1}_{operator}_{col2}", failed_count))
else:
    print(f"  PASS: All records satisfy '{col1}' {operator} '{col2}'.")
"""

    code += """
print("\n--- Data Quality Summary ---")
if all_failed_records:
    print("The following data quality rules failed:")
    for rule_name, failed_count in all_failed_records:
        print(f"- {rule_name}: {failed_count} failures")
else:
    print("All data quality rules passed!")

spark.stop()
print("Spark session stopped.")
"""
    return code
