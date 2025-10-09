# Data Accuracy Comparison Fixes

## Summary of Changes

This PR fixes two critical issues in the Data Accuracy comparison tool:

1. **Original Key Values Preservation**: Key values in difference reports now show original values instead of normalized values
2. **CSV Download Functionality**: Improved download mechanism to work reliably across all browsers

## Issues Fixed

### Issue 1: Normalized Key Values in Differences

**Problem**: When comparing datasets with multiple key columns (e.g., ano, mes, uf), the differences table was showing normalized values (lowercase, no accents) instead of the original values.

**Example**:
- Original value: `UF = "RJ"`
- What was shown: `uf = "rj"` (normalized)
- What should show: `uf = "RJ"` (original)

**Root Cause**: The code was extracting key values from the normalized composite key string (`composite_key.split("||")`) instead of from the original dataframe.

**Solution**: 
- Modified the merge operation to include original key columns from the GOLD dataset
- Updated difference recording to extract original values from the merged dataframe
- Added proper type conversion for different data types (int, float, str)

**Code Changes** (`src/accuracy/processor.py`):
```python
# Before: Only merged value columns
merged = pd.merge(
    target_df,
    gold_df[["__composite_key__"] + value_columns],
    ...
)

# After: Also include original key columns
gold_merge_cols = ["__composite_key__"] + key_columns + value_columns
merged = pd.merge(
    target_df,
    gold_df[gold_merge_cols],
    ...
)

# Before: Extracted from normalized composite key
key_values = {
    key_columns[i]: composite_key.split("||")[i]
    for i in range(len(key_columns))
}

# After: Extract from original dataframe with type conversion
key_values = {}
for key_col in key_columns:
    if f"{key_col}_target" in row.index:
        original_value = row[f"{key_col}_target"]
    elif key_col in row.index:
        original_value = row[key_col]
    else:
        original_value = composite_key.split("||")[key_columns.index(key_col)]
    
    # Convert to native Python type for JSON serialization
    if pd.isna(original_value):
        key_values[key_col] = None
    elif isinstance(original_value, (np.integer, np.int64, np.int32)):
        key_values[key_col] = int(original_value)
    elif isinstance(original_value, (np.floating, np.float64, np.float32)):
        key_values[key_col] = float(original_value)
    else:
        key_values[key_col] = original_value
```

### Issue 2: CSV Download Not Working

**Problem**: Clicking the "Download CSV" button was not triggering the file download properly.

**Root Cause**: The original implementation used a simple anchor tag with `link.download` attribute, which doesn't work reliably for cross-origin requests or when the browser doesn't properly detect the content type.

**Solution**:
- Fetch the file as a Blob before triggering download
- Create a temporary Blob URL and trigger download from it
- Added explicit MIME types in the backend for CSV and JSON files
- Proper cleanup of Blob URLs after download

**Code Changes**:

**Frontend** (`frontend//src/hooks/useDataAccuracy.js`):
```javascript
// Before: Simple link download
const downloadFile = useCallback((url) => {
  const link = document.createElement('a');
  link.href = url;
  link.download = url.split('/').pop();
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}, []);

// After: Blob-based download
const downloadFile = useCallback(async (url) => {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error('Download failed');
    }
    
    const blob = await response.blob();
    const filename = url.split('/').pop();
    
    const blobUrl = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    
    document.body.removeChild(link);
    window.URL.revokeObjectURL(blobUrl);
  } catch (err) {
    setError(`Failed to download file: ${err.message}`);
    console.error('Download error:', err);
  }
}, []);
```

**Backend** (`src/accuracy/routes.py`):
```python
# Added explicit MIME types for downloads
if filename.endswith('.csv'):
    mimetype = 'text/csv'
elif filename.endswith('.json'):
    mimetype = 'application/json'
else:
    mimetype = 'application/octet-stream'

return send_file(
    file_path, 
    as_attachment=True, 
    download_name=filename,
    mimetype=mimetype
)
```

## Testing

### New Test Suite (`tests/test_accuracy_multiple_keys.py`)

Created comprehensive tests for multiple key column scenarios:

1. **test_original_key_values_preserved**: Verifies original key values are preserved with normalization enabled
2. **test_three_key_columns_with_many_value_columns**: Tests scenario similar to user's case (3 keys, many value columns)
3. **test_composite_key_with_special_characters**: Tests keys with accents and special characters

### Test Results

All 34 accuracy tests pass:
- ✅ 9 backend tests (`test_accuracy_backend.py`)
- ✅ 4 integration tests (`test_accuracy_integration.py`)
- ✅ 18 robust integration tests (`test_accuracy_integration_robust.py`)
- ✅ 3 new multiple key tests (`test_accuracy_multiple_keys.py`)

### Manual Testing

Run the demonstration script to see the fix in action:
```bash
python3 tests/manual_test_user_scenario.py
```

This script reproduces the user's scenario and verifies:
- Original key values are preserved (e.g., "RJ" not "rj")
- Proper data types (integers remain integers, not strings)
- Correct identification of differences
- Accurate correction of values

## User Impact

### Before the Fix
- Users saw confusing normalized values in the differences table
- UF column would show "rj", "sp", "mg" instead of "RJ", "SP", "MG"
- Integer columns would be shown as strings
- CSV downloads might not trigger in some browsers

### After the Fix
- Original values are displayed exactly as they appear in the source data
- Proper data types are maintained
- Downloads work reliably across all browsers
- Clear, accurate reporting of differences

## Example Output

When comparing datasets with keys `(Ano=2023, Mês=1, UF="RJ")`:

**Before**:
```
Keys: {"ano": "2023", "mes": "1", "uf": "rj"}
```

**After**:
```
Keys: {"ano": 2023, "mes": 1, "uf": "RJ"}
```

## Files Modified

1. `src/accuracy/processor.py` - Core comparison logic
2. `src/accuracy/routes.py` - Download endpoint with MIME types
3. `frontend//src/hooks/useDataAccuracy.js` - Download functionality
4. `tests/test_accuracy_multiple_keys.py` - New test suite (created)
5. `tests/manual_test_user_scenario.py` - Manual demonstration script (created)

## Backward Compatibility

These changes are fully backward compatible. Existing functionality is preserved, and the fixes only improve the accuracy and reliability of the comparison tool.
