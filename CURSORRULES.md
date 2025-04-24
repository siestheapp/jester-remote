# Cursor Development Rules for Jester

These rules ensure consistent, maintainable, and well-documented code development in the Cursor environment.

## 📝 Documentation Integration

1. **Changelog Updates**
   - Add significant changes to CHANGELOG.md under [Unreleased]
   - Follow Keep a Changelog format (Added, Changed, Deprecated, Removed, Fixed)
   - Include PR/issue numbers in changelog entries
   - Update version numbers according to semver

2. **README Synchronization**
   - Keep code examples in README.md up to date
   - Update architecture diagrams when structure changes
   - Maintain accurate dependency lists
   - Document new features in appropriate sections

3. **API Documentation**
   - Update docs/api/README.md for endpoint changes
   - Include request/response examples
   - Document breaking changes
   - Keep OpenAPI/Swagger specs current

## 🚫 Non-Destructive Operations

1. **File Management**
   - Never delete files directly; move to app/deprecated/
   - Include deprecation notice with date and reason
   - Document replacement locations
   - Keep clear migration paths

2. **Code Evolution**
   - Use feature flags for gradual rollouts
   - Maintain backward compatibility
   - Version APIs appropriately
   - Document breaking changes

## 🏗️ Code Structure

1. **Model/Schema Organization**
   - Place Pydantic models in app/models/
   - Keep API schemas in app/schemas/
   - Maintain separation of concerns
   - Follow established naming conventions

2. **Type Safety**
   - Use type hints consistently
   - Include validation rules in models
   - Document expected types
   - Handle edge cases explicitly

## 📊 Testing Requirements

1. **Test Coverage**
   - Write tests before implementing features
   - Include both unit and integration tests
   - Test edge cases and error conditions
   - Maintain minimum 80% coverage

2. **Test Organization**
   - Mirror production code structure in tests/
   - Use descriptive test names
   - Include setup and teardown
   - Document test data and fixtures

## 🔄 Version Control

1. **Commit Messages**
   - Follow conventional commits (feat:, fix:, docs:, etc.)
   - Include scope when relevant
   - Reference issues/PRs
   - Provide clear descriptions

2. **Branch Management**
   - Create feature branches from main
   - Keep branches focused and small
   - Rebase before merging
   - Delete branches after merge

## 🎯 Code Quality

1. **Style Guidelines**
   - Follow PEP 8
   - Use Black for formatting
   - Maximum line length: 88 characters
   - Consistent import ordering

2. **Code Organization**
   - One class/function per file when practical
   - Clear module hierarchy
   - Logical file naming
   - Consistent directory structure

## 🔒 Security Practices

1. **Sensitive Data**
   - Use environment variables for secrets
   - Never commit API keys or credentials
   - Document security requirements
   - Follow least privilege principle

2. **Error Handling**
   - Use appropriate exception types
   - Include error context
   - Log security events
   - Sanitize error responses

## 🚀 Performance

1. **Resource Management**
   - Close file handles and connections
   - Use context managers
   - Implement proper cleanup
   - Monitor memory usage

2. **Optimization**
   - Profile before optimizing
   - Document performance requirements
   - Use appropriate data structures
   - Consider scalability

## 📦 Dependencies

1. **Package Management**
   - Pin dependency versions
   - Document requirements
   - Regular security updates
   - Minimize dependencies

2. **Virtual Environments**
   - Use venv for isolation
   - Document setup steps
   - Include all requirements
   - Separate dev dependencies

## 🤝 Collaboration

1. **Code Review**
   - Request reviews from relevant team members
   - Address all comments
   - Explain complex changes
   - Update documentation

2. **Knowledge Sharing**
   - Document architectural decisions
   - Update wiki/docs
   - Share learning in comments
   - Maintain troubleshooting guides

Remember: These rules ensure code quality, maintainability, and team efficiency. When in doubt, prioritize clarity and documentation over cleverness. 