# Development Notes

Personal development notes and guidelines for this project.

## 🚀 Quick Setup

### Prerequisites

- Python 3.8 or higher
- pip
- Virtual environment (recommended)

### Development Setup

1. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov  # For testing
   ```

3. **Set Up Environment:**
   ```bash
   cp secure_env_example.txt .env
   # Edit .env with your API keys
   ```

4. **Run Tests:**
   ```bash
   python tests/run_tests.py --fast
   ```

## 📁 Project Structure

```
CLIP_Analysis/
├── src/                        # Main source code
│   ├── analyzers/              # Analysis modules (CLIP, LLM, metadata)
│   ├── config/                 # Configuration management
│   ├── database/               # Database operations
│   ├── processors/             # Batch processing
│   ├── routes/                 # Web routes
│   ├── services/               # Business logic
│   ├── utils/                  # Utility functions
│   └── viewers/                # Web interface
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/           # Integration tests
│   └── misc/                   # Miscellaneous tests
├── scripts/                    # Utility scripts
└── main.py                     # CLI entry point
```

## 🧪 Testing

Run tests with the unified test runner:

```bash
# Run all tests
python tests/run_tests.py

# Run specific test suites
python tests/run_tests.py --unit          # Unit tests only
python tests/run_tests.py --integration   # Integration tests
python tests/run_tests.py --fast          # Quick tests only
python tests/run_tests.py --coverage      # With coverage report
```

## 🔧 Code Quality

### Pre-commit Hooks (Optional)

If you want automatic code quality checks:

```bash
pip install pre-commit
pre-commit install
```

This will automatically run:
- Ruff (linter and formatter)
- Basic file checks (trailing whitespace, etc.)
- Security checks (Bandit)

### Manual Code Quality

```bash
# Format code
ruff format src/

# Lint code
ruff check src/

# Type checking (optional)
mypy src/ --ignore-missing-imports
```

## 📝 Development Workflow

1. **Make Changes:**
   - Write code following existing patterns
   - Add type hints where possible
   - Add docstrings for new functions/classes

2. **Test Your Changes:**
   ```bash
   python tests/run_tests.py --fast
   ```

3. **Commit:**
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

## 🏗️ Architecture Notes

### Key Design Patterns

- **Dependency Injection**: Core classes accept dependencies for better testability
- **Service Layer**: Business logic separated from presentation
- **Centralized Utilities**: Common operations in `src/utils/`
- **Type Hints**: Comprehensive type annotations throughout

### Adding New Features

1. **New Analyzer:**
   - Add to `src/analyzers/`
   - Follow existing patterns (see `clip_analyzer.py` or `llm_analyzer.py`)
   - Add tests in `tests/unit/`

2. **New Service:**
   - Add to `src/services/`
   - Follow existing service patterns
   - Add tests

3. **New Route:**
   - Add to `src/routes/`
   - Register in `src/viewers/web_interface.py`
   - Add tests

## 🐛 Debugging

### Logging

The project uses centralized logging:

```python
from src.utils.logger import get_global_logger

logger = get_global_logger()
logger.info("Message")
logger.error("Error message")
```

Logs are written to:
- `logs/app.log` - General application logs
- `logs/errors.log` - Error logs
- `logs/processing.log` - Processing logs

### Debug Mode

Enable debug mode in `.env`:
```bash
DEBUG=True
```

Or in code:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📦 Building

To build the package (if needed):

```bash
python setup.py sdist bdist_wheel
```

## 🔄 Common Tasks

### Update Dependencies

```bash
pip install --upgrade -r requirements.txt
```

### Clean Build Artifacts

```bash
rm -rf build/ dist/ *.egg-info/
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

### Database Management

```bash
# Check database
python scripts/check_db.py

# Clear database (if needed)
python main.py database clear
```

## 📚 Useful Resources

- `CONFIG.md` - Complete configuration guide
- `CLIP_API.md` - CLIP API setup and usage
- Test files in `tests/` - Examples of how to use the code

