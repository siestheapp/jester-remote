# Contributing to Jester

Thank you for your interest in contributing to Jester! This document provides guidelines and instructions for contributing.

## 🎯 Development Process

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/jester.git
   cd jester
   git remote add upstream https://github.com/siestheapp/jester.git
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Development Guidelines**
   - Follow [CURSORRULES.md](CURSORRULES.md)
   - Use type hints
   - Write docstrings
   - Include tests
   - Update documentation

4. **Code Style**
   - Use Black for formatting
   - Follow PEP 8
   - Maximum line length: 88 characters
   - Use meaningful variable names

## 🧪 Testing

1. **Running Tests**
   ```bash
   # Run all tests
   pytest tests/

   # Run specific test file
   pytest tests/test_vector_search.py

   # Run with coverage
   pytest --cov=app tests/
   ```

2. **Writing Tests**
   - Place tests in `tests/` directory
   - Match production file structure
   - Use descriptive test names
   - Include both positive and negative cases

## 📝 Documentation

1. **Code Documentation**
   - Use docstrings for all public functions/classes
   - Include type hints
   - Provide usage examples
   - Document exceptions

2. **Project Documentation**
   - Update README.md for major changes
   - Document new features in docs/
   - Keep architecture diagrams current
   - Update API documentation

## 🔄 Pull Request Process

1. **Before Submitting**
   - Run all tests
   - Update documentation
   - Format code with Black
   - Check type hints with mypy

2. **PR Description**
   - Clear description of changes
   - Link related issues
   - Include test results
   - List breaking changes

3. **Review Process**
   - Address review comments
   - Keep PR focused
   - Rebase if needed
   - Squash commits

## 🐛 Bug Reports

1. **Before Reporting**
   - Check existing issues
   - Try latest version
   - Verify configuration

2. **Report Content**
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information

## 🚀 Feature Requests

1. **Proposal**
   - Clear use case
   - Expected behavior
   - Example usage
   - Implementation ideas

2. **Discussion**
   - Open for feedback
   - Consider alternatives
   - Discuss trade-offs

## 📦 Release Process

1. **Version Numbers**
   - Follow semantic versioning
   - Document changes in CHANGELOG.md
   - Tag releases

2. **Release Steps**
   - Update version numbers
   - Update documentation
   - Create release notes
   - Tag and push

## 🤝 Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow project guidelines

## 📄 License

By contributing, you agree that your contributions will be licensed under the project's license. 