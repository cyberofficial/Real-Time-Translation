# Contributing to Synthalingua

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  - [Development Setup](#development-setup)
  - [Branching Strategy](#branching-strategy)
- [Making Contributions](#making-contributions)
  - [Code Contributions](#code-contributions)
  - [Documentation](#documentation)
  - [Pull Requests](#pull-requests)
  - [Commit Guidelines](#commit-guidelines)
- [Issue Guidelines](#issue-guidelines)
  - [Bug Reports](#bug-reports)
  - [Feature Requests](#feature-requests)
- [Technical Guidelines](#technical-guidelines)
  - [Code Style](#code-style)
  - [Testing Requirements](#testing-requirements)

## Code of Conduct
- Maintain respectful and professional communication
- Be open to collaboration and constructive feedback
- Foster an inclusive environment where everyone feels welcome
- Help others and share knowledge when possible

## Getting Started

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/Synthalingua.git`
3. Add upstream remote: `git remote add upstream https://github.com/cyberofficial/Synthalingua.git`
4. Create a virtual environment: `python -m venv venv`
5. Activate environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
6. Install dependencies: `pip install -r requirements_dev.txt`

### Branching Strategy
- `master` - Production-ready code
- `develop` - Integration branch for features
- Feature branches: `feature/your-feature-name`
- Bug fix branches: `fix/issue-description`
- Format: `type/short-description`

## Making Contributions

### Code Contributions
**IMPORTANT**: I do not accept AI-generated code. All contributions must be human-written code.

1. Ensure your code:
   - Meets our minimum Python version requirements
   - Includes appropriate error handling
   - Is well-documented with docstrings
   - Follows our code style guidelines
   - Includes necessary unit tests

2. Before submitting:
   - Run all tests locally
   - Update documentation if needed
   - Ensure your branch is up to date with develop

### Documentation
- Use clear, concise language
- Include code examples where appropriate
- Update relevant README sections
- Add docstrings to new functions/classes
- Keep documentation in sync with code changes

### Pull Requests
1. Create focused PRs (one feature/fix per PR)
2. Use descriptive titles: `[Type] Brief description`
3. Include in description:
   - What changes were made
   - Why changes were necessary
   - How to test the changes
   - Related issue numbers
4. Link relevant issues
5. Update tests and documentation
6. Ensure CI checks pass

### Commit Guidelines
Format: `type(scope): description`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Testing changes
- `chore`: Maintenance tasks

Example: `feat(audio): add new transcription format support`

## Issue Guidelines

### Bug Reports
Include:
1. Steps to reproduce
2. Expected behavior
3. Actual behavior
4. System information:
   - OS version
   - Python version
   - Synthalingua version
5. Screenshots/logs if applicable
6. Sample code demonstrating the issue

### Feature Requests
Include:
1. Clear description of the feature
2. Use case and benefits
3. Potential implementation approach
4. Any relevant examples

## Technical Guidelines

### Code Style
- Follow PEP 8 conventions
- Use meaningful variable/function names
- Keep functions focused and small
- Use type hints where possible
- Maximum line length: 100 characters
- Use descriptive docstrings

### Testing Requirements
- Include unit tests for new features
- Maintain or improve code coverage
- Test edge cases and error conditions
- Include integration tests where needed
- Verify backward compatibility
