# Deprecated Directory

This directory contains deprecated code that has been replaced by newer implementations.

## Purpose
- Maintain code history
- Provide reference for previous implementations
- Allow safe transitions to new code
- Follow non-destructive operation principles

## Guidelines
1. Never delete files; move them here instead
2. Add a deprecation notice at the top of each file
3. Document replacement locations
4. Keep directory organized by feature/module

## File Naming
- Append version to original filename (e.g., `jester_chat_v1.py`)
- Include deprecation date in filename
- Maintain original directory structure within deprecated/

## Documentation Requirements
Each deprecated file should include:
1. Deprecation date
2. Reason for deprecation
3. Location of new implementation
4. Migration guide if applicable 