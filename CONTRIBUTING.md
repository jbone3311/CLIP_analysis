# Contributing to CLIP Analysis

Thank you for your interest in contributing to the CLIP Analysis project! This document provides guidelines and information for contributors.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of the project structure

### Development Setup

1. **Fork and Clone:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/CLIP_analysis.git
   cd CLIP_analysis
   ```

2. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment:**
   ```bash
   cp secure_env_example.txt .env
   # Edit .env with your API keys (optional for development)
   ```

5. **Run Tests:**
   ```bash
   python tests/run_tests.py --fast
   ```

## 📁 Project Structure

Understanding the project structure is crucial for effective contributions:

```
CLIP_Analysis/
├── src/                        # Main source code
│   ├── analyzers/              # Analysis modules (CLIP, LLM, metadata)
│   ├── config/                 # Configuration management
│   ├── database/               # Database operations
│   ├── processors/             # Batch processing (with DI)
│   ├── routes/                 # Web routes and API endpoints
│   ├── services/               # Business logic services
│   ├── utils/                  # Utility functions
│   └── viewers/                # Web interface
├── tests/                      # Test suite
│   ├── run_tests.py           # Unified test runner
│   ├── unit/                   # Unit tests
│   ├── integration/           # Integration tests
│   └── misc/                   # Miscellaneous tests
├── scripts/                    # Utility scripts
├── logs/                       # Application logs
└── .project-specific/          # AI memory and tracking docs
```

## 🏗️ Architecture Principles

This project follows modern software engineering practices:

### Dependency Injection
Core classes use dependency injection for better testability:

```python
# Good: Dependency injection
class DirectoryProcessor:
    def __init__(self, config, db_manager=None, llm_manager=None):
        self.db_manager = db_manager or DatabaseManager()
        self.llm_manager = llm_manager or LLMManager()

# Usage
processor = DirectoryProcessor(config, mock_db, mock_llm)  # For testing
processor = DirectoryProcessor(config)  # For production
```

### Centralized Utilities
Use centralized utilities instead of duplicating code:

```python
# Good: Use centralized utilities
from src.utils import compute_file_hash, ProgressTracker

md5_hash = compute_file_hash(file_path, algorithm='md5')
tracker = ProgressTracker(total=100, callback=print)

# Avoid: Duplicating utility code
```

### Type Hints
Always add type hints to new code:

```python
def process_image(
    self, 
    image_file: str, 
    progress_tracker: Optional[ProgressTracker] = None
) -> bool:
    """Process a single image and return success status."""
    pass
```

## 🧪 Testing

### Running Tests

The project uses a unified test runner with flexible options:

```bash
# Run all tests
python tests/run_tests.py

# Run specific test suites
python tests/run_tests.py --unit          # Unit tests only
python tests/run_tests.py --integration   # Integration tests
python tests/run_tests.py --web           # Web interface tests
python tests/run_tests.py --fast          # Quick tests only
python tests/run_tests.py --verbose      # Verbose output
python tests/run_tests.py --coverage      # With coverage report
```

### Writing Tests

#### Unit Tests
Place unit tests in `tests/unit/`:

```python
# tests/unit/test_my_module.py
import unittest
from unittest.mock import Mock, patch
from src.my_module import MyClass

class TestMyClass(unittest.TestCase):
    def setUp(self):
        self.mock_dependency = Mock()
        self.instance = MyClass(dependency=self.mock_dependency)
    
    def test_method_returns_expected_result(self):
        result = self.instance.my_method()
        self.assertEqual(result, expected_value)
```

#### Integration Tests
Place integration tests in `tests/integration/`:

```python
# tests/integration/test_my_integration.py
import pytest
from src.processors import DirectoryProcessor

def test_end_to_end_processing():
    # Test complete workflow
    pass
```

#### Test Guidelines
- Use dependency injection for testable code
- Mock external dependencies (APIs, databases, file systems)
- Test both success and failure cases
- Use descriptive test names
- Keep tests fast and isolated

## 📝 Code Style

### Python Style
- Follow PEP 8 guidelines
- Use type hints for all public methods
- Write descriptive docstrings
- Use meaningful variable names

### Import Style
Use absolute imports from `src`:

```python
# Good
from src.utils import compute_file_hash
from src.processors import DirectoryProcessor

# Avoid
from ..utils import compute_file_hash
from .directory_processor import DirectoryProcessor
```

### Documentation
- Add docstrings to all public methods
- Include type hints
- Document complex algorithms
- Update README.md for user-facing changes

## 🔧 Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Write code following project conventions
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes
```bash
# Run all tests
python tests/run_tests.py

# Run specific tests
python tests/run_tests.py --unit
```

### 4. Commit Changes
```bash
git add .
git commit -m "Add feature: brief description

- Detailed description of changes
- Any breaking changes
- Related issues"
```

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information:**
   - Python version
   - Operating system
   - Dependencies versions

2. **Steps to Reproduce:**
   - Clear, numbered steps
   - Expected vs actual behavior
   - Error messages (if any)

3. **Additional Context:**
   - Screenshots (if applicable)
   - Log files (check `logs/` directory)
   - Configuration files (remove sensitive data)

## ✨ Feature Requests

When requesting features:

1. **Describe the Problem:**
   - What problem does this solve?
   - Who would benefit from this feature?

2. **Propose a Solution:**
   - How should this feature work?
   - Any implementation ideas?

3. **Consider Alternatives:**
   - Are there existing workarounds?
   - Could this be solved differently?

## 📋 Pull Request Guidelines

### Before Submitting
- [ ] Code follows project conventions
- [ ] Tests pass: `python tests/run_tests.py`
- [ ] Type hints added to new code
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes
```

## 🏷️ Release Process

### Version Numbering
We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Changelog
Update `CHANGELOG.md` for all releases:
- Group changes by type (Added, Changed, Fixed, Removed)
- Include migration instructions for breaking changes
- Reference issues and PRs

## 🤝 Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inclusive environment for all contributors.

### Expected Behavior
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Respect different viewpoints

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or inflammatory comments
- Personal attacks
- Any unprofessional conduct

## 📞 Getting Help

### Documentation
- Check `README.md` for general usage
- Review `.project-specific/` for detailed docs
- Look at test files for usage examples

### Community
- Create an issue for questions
- Use GitHub Discussions for general topics
- Check existing issues before creating new ones

### Development Questions
- Review the codebase structure
- Check existing tests for patterns
- Look at similar implementations

## 🎯 Areas for Contribution

### High Priority
- **Test Coverage**: Add tests for untested modules
- **Performance**: Optimize slow operations
- **Documentation**: Improve user guides
- **Error Handling**: Enhance error messages

### Medium Priority
- **New Features**: Additional analysis modes
- **UI Improvements**: Web interface enhancements
- **Utilities**: Additional helper functions
- **Integration**: New LLM providers

### Low Priority
- **Code Style**: Minor style improvements
- **Documentation**: Typos and clarifications
- **Examples**: Additional usage examples
- **Tools**: Development tooling improvements

## 🏆 Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- Project documentation

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

**Thank you for contributing to CLIP Analysis!** 🎉

Your contributions help make this project better for everyone. If you have any questions about contributing, please don't hesitate to ask!
