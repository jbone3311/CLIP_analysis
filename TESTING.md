# Testing Guide for Image Analysis Project

This document provides comprehensive information about testing the dual-mode image analysis tool.

## 📋 Overview

The test suite covers all aspects of the image analysis system:

- **LLM Analysis** (`analysis_LLM.py`)
- **CLIP Interrogator Analysis** (`analysis_interrogate.py`)
- **Configuration Management** (`config.py`)
- **Database Utilities** (`db_utils.py`)
- **Utility Functions** (`utils.py`)
- **Batch Processing** (`directory_processor.py`)
- **Integration Tests** (End-to-end workflows)

## 🚀 Quick Start

### Installation

1. **Install test dependencies:**
   ```bash
   pip install -r requirements-test.txt
   ```

2. **Run all tests:**
   ```bash
   python run_tests.py
   ```

3. **Run with coverage:**
   ```bash
   python run_tests.py --coverage
   ```

### Basic Commands

```bash
# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --unit

# Run only integration tests
python run_tests.py --integration

# Run tests for specific module
python run_tests.py --module config

# Verbose output
python run_tests.py --verbose

# Check test structure
python run_tests.py --check
```

## 🧪 Test Structure

### Test Files

| File | Description | Coverage |
|------|-------------|----------|
| `conftest.py` | Test configuration and fixtures | Test setup, mock data |
| `test_analysis_llm.py` | LLM analysis module tests | API calls, prompt processing, error handling |
| `test_analysis_interrogate.py` | CLIP interrogator tests | Image encoding, API interactions, modes |
| `test_config.py` | Configuration management tests | Environment variables, validation |
| `test_db_utils.py` | Database utilities tests | CRUD operations, concurrency, errors |
| `test_utils.py` | Utility functions tests | File operations, unique codes, JSON handling |
| `test_directory_processor.py` | Batch processing tests | Directory traversal, subprocess management |
| `test_integration.py` | End-to-end integration tests | Complete workflows, CLI testing |

### Test Categories

#### Unit Tests
- **Individual function testing**
- **Mocked external dependencies**
- **Fast execution**
- **Isolated components**

#### Integration Tests
- **Complete workflow testing**
- **Real API interactions (mocked)**
- **Cross-module functionality**
- **End-to-end scenarios**

## 🛠️ Test Fixtures and Utilities

### Available Fixtures

```python
# Basic fixtures
temp_dir               # Temporary directory for test files
sample_image_path      # Sample JPEG test image
sample_png_image_path  # Sample PNG test image
multiple_test_images   # List of test images

# Configuration fixtures
sample_env_file        # Sample .env configuration
sample_llm_prompts     # Sample LLM_Prompts.json

# Mock data fixtures
mock_clip_response     # Mock CLIP API response
mock_llm_response      # Mock LLM API response
mock_database          # Mock SQLite database
image_base64           # Base64 encoded test image

# Output fixtures
sample_json_output     # Sample analysis output JSON
```

### Using Fixtures

```python
def test_my_function(temp_dir, sample_image_path, mock_llm_response):
    """Example test using fixtures."""
    # temp_dir is automatically created and cleaned up
    # sample_image_path contains a valid test image
    # mock_llm_response contains realistic API response data
    pass
```

## 🔧 Test Configuration

### Environment Variables

Tests use specific environment variables to avoid interfering with production:

```bash
TESTING=true
PYTHONPATH=/path/to/project
LOG_LEVEL=WARNING
```

### Mock Configuration

API calls are mocked using the `responses` library:

```python
@responses.activate
def test_api_call():
    responses.add(
        responses.POST,
        "https://api.example.com/endpoint",
        json={"result": "success"},
        status=200
    )
    # Test code here
```

## 📊 Coverage Reports

### Generating Coverage

```bash
# HTML coverage report
python run_tests.py --coverage

# View report
open htmlcov/index.html
```

### Coverage Targets

| Module | Target Coverage | Current Status |
|--------|----------------|----------------|
| `analysis_LLM.py` | >90% | ✅ |
| `analysis_interrogate.py` | >90% | ✅ |
| `config.py` | >95% | ✅ |
| `db_utils.py` | >85% | ✅ |
| `utils.py` | >95% | ✅ |
| `directory_processor.py` | >80% | ✅ |

## 🧩 Test Examples

### Unit Test Example

```python
def test_generate_unique_code_consistent(sample_image_path):
    """Test that unique code generation is consistent."""
    code1 = generate_unique_code(sample_image_path)
    code2 = generate_unique_code(sample_image_path)
    
    assert code1 == code2
    assert isinstance(code1, str)
    assert len(code1) > 0
```

### Integration Test Example

```python
@responses.activate
def test_complete_workflow(sample_image_path, temp_dir, mock_llm_response):
    """Test complete LLM analysis workflow."""
    responses.add(
        responses.POST,
        "https://api.openai.com/v1/chat/completions",
        json=mock_llm_response,
        status=200
    )
    
    result = subprocess.run([
        "python", "analysis_LLM.py",
        sample_image_path,
        "--prompt", "PROMPT1",
        "--model", "1"
    ], capture_output=True, text=True)
    
    assert result.returncode == 0
```

### Mock Test Example

```python
@patch('requests.post')
def test_api_error_handling(mock_post, sample_image_path):
    """Test API error handling."""
    mock_post.side_effect = requests.RequestException("Network error")
    
    analyzer = LLMAnalyzer("https://api.test.com", "key", "model")
    
    # Should handle error gracefully
    analyzer.process_image(sample_image_path, ["PROMPT1"])
```

## 🚨 Common Test Patterns

### Testing Configuration

```python
@patch.dict(os.environ, {
    'API_BASE_URL': 'http://test:8080',
    'ENABLE_CLIP_ANALYSIS': 'true'
})
def test_config_loading():
    config = Config()
    assert config.api_base_url == 'http://test:8080'
    assert config.enable_clip_analysis is True
```

### Testing File Operations

```python
def test_json_operations(temp_dir):
    test_data = {"key": "value"}
    file_path = os.path.join(temp_dir, "test.json")
    
    save_json(test_data, file_path)
    loaded_data = load_json(file_path)
    
    assert loaded_data == test_data
```

### Testing Database Operations

```python
def test_database_operations(mock_database):
    db = Database(mock_database)
    
    # Add test data
    db.add_image("unique123", "test.jpg", 1699999999.0, 1024)
    
    # Verify data
    image_id = db.get_image_id_db("unique123")
    assert image_id is not None
    
    db.close()
```

## 🔍 Debugging Tests

### Running Specific Tests

```bash
# Run single test file
python -m pytest test_config.py -v

# Run specific test
python -m pytest test_config.py::TestConfigDefaults::test_config_defaults -v

# Run tests matching pattern
python -m pytest -k "test_config" -v
```

### Debug Output

```bash
# Enable debug logging
python run_tests.py --verbose

# Capture print statements
python -m pytest -s test_file.py

# Drop into debugger on failure
python -m pytest --pdb test_file.py
```

### Common Issues

1. **Import Errors**: Ensure `PYTHONPATH` includes project directory
2. **Missing Dependencies**: Run `pip install -r requirements-test.txt`
3. **API Mocking**: Verify `@responses.activate` decorator is used
4. **File Permissions**: Check temp directory permissions on different OS

## 📈 Performance Testing

### Benchmark Tests

```python
import time

def test_performance_bulk_processing(multiple_test_images):
    """Test performance of bulk image processing."""
    start_time = time.time()
    
    # Process multiple images
    for image_path in multiple_test_images:
        unique_code = generate_unique_code(image_path)
    
    elapsed = time.time() - start_time
    
    # Should process 4 images in under 1 second
    assert elapsed < 1.0
```

### Memory Testing

```python
import psutil
import os

def test_memory_usage():
    """Test memory usage doesn't exceed limits."""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Perform memory-intensive operation
    large_data = generate_large_test_data()
    
    current_memory = process.memory_info().rss
    memory_increase = current_memory - initial_memory
    
    # Should not increase memory by more than 100MB
    assert memory_increase < 100 * 1024 * 1024
```

## 🔄 Continuous Integration

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: |
        python run_tests.py --coverage
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## 📝 Adding New Tests

### Test Checklist

When adding new functionality, ensure you add:

- [ ] Unit tests for individual functions
- [ ] Integration tests for workflows
- [ ] Error handling tests
- [ ] Configuration tests (if applicable)
- [ ] Mock tests for external dependencies
- [ ] Performance tests (if relevant)

### Test Template

```python
import pytest
from unittest.mock import patch, Mock
from your_module import YourClass

class TestYourClass:
    """Test cases for YourClass."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        instance = YourClass()
        result = instance.method()
        assert result == expected_value
    
    def test_error_handling(self):
        """Test error handling."""
        instance = YourClass()
        with pytest.raises(ExpectedException):
            instance.method_that_should_fail()
    
    @patch('your_module.external_dependency')
    def test_with_mock(self, mock_dependency):
        """Test with mocked dependency."""
        mock_dependency.return_value = "mocked_result"
        instance = YourClass()
        result = instance.method_using_dependency()
        assert result == "expected_result"
```

## 🆘 Troubleshooting

### Common Test Failures

1. **File Not Found**: Check if test files exist and paths are correct
2. **Permission Denied**: Ensure test directories are writable
3. **Import Errors**: Verify module paths and Python path
4. **API Errors**: Check mock configurations and responses
5. **Database Errors**: Ensure database files are accessible

### Getting Help

1. **Check logs**: Look at test output for specific error messages
2. **Verify setup**: Run `python run_tests.py --check`
3. **Isolate tests**: Run individual test files to identify issues
4. **Check fixtures**: Verify test fixtures are working correctly

---

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [responses Library](https://github.com/getsentry/responses)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)

---

*For questions about testing, check the project documentation or create an issue in the repository.*