# Cursor Development Rules for Jester

## 🚫 Destructive Operations

1. **Never Perform Destructive Git Operations**
   - Avoid `git filter-repo`, `git filter-branch`, or similar history-altering commands
   - Instead of deleting sensitive data, rotate credentials and commit the change
   - Use `.gitignore` to prevent future commits of sensitive files
   - For large files, consider Git LFS instead of removal

2. **Safe File Management**
   - Never delete files directly; move them to a deprecated folder if needed
   - Document why files are being moved/deprecated in commit messages
   - Keep a clear trail of code evolution
   - Use clear naming for replacements (e.g., `user_service_v2.py`)

## 🏗️ Code Organization

1. **File Structure**
   - Keep related files together in appropriate modules
   - Use clear, descriptive file names
   - Maintain a logical directory structure
   - Document module purposes in README files

2. **Code Migration**
   - When replacing functionality, keep old version until new is proven
   - Use feature flags for gradual rollouts
   - Maintain backwards compatibility where possible
   - Document migration paths clearly

## 📝 Documentation

1. **Code Comments**
   - Document why, not what
   - Keep comments up to date
   - Use docstrings for all public functions
   - Include examples for complex functionality

2. **Change Documentation**
   - Write clear commit messages
   - Update README.md when adding features
   - Document breaking changes prominently
   - Keep CHANGELOG.md up to date

## 🔒 Security

1. **Sensitive Data**
   - Never commit API keys or credentials
   - Use environment variables for configuration
   - Keep secrets in a secure vault
   - Document security-related configuration

## 🧪 Testing

1. **Test Coverage**
   - Write tests before deleting/deprecating code
   - Maintain high test coverage
   - Include integration tests
   - Test edge cases thoroughly

## 🤝 Collaboration

1. **Code Review**
   - Get approval before significant changes
   - Document decisions in PR descriptions
   - Use draft PRs for work in progress
   - Respond to review comments promptly

## 🚀 Deployment

1. **Release Process**
   - Use semantic versioning
   - Test in staging before production
   - Document deployment steps
   - Have rollback plans ready

## 🔄 Version Control

1. **Branch Management**
   - Create feature branches for changes
   - Keep branches up to date with main
   - Delete branches after merging
   - Use meaningful branch names

Remember: The goal is to maintain a stable, reliable, and maintainable codebase. When in doubt, choose the safer, more documented approach over quick fixes. 