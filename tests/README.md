# Voting System Test Suite

This directory contains comprehensive tests for the Voting System application, ensuring it meets quality requirements in maintainability, reliability, performance, and security.

## Test Structure

- `unit/`: Unit tests for individual components
- `integration/`: Tests for API endpoints and component integration
- `performance/`: Load and performance tests using Locust
- `security/`: Security and penetration tests
- `ui/`: Selenium-based UI tests for frontend

## Running Tests

### Install dependencies

Make sure all dependencies are installed:

```
poetry install
```

### Run all tests

```
poetry run pytest
```

### Run specific test categories

```
# Unit tests only
poetry run pytest tests/unit

# Integration tests
poetry run pytest tests/integration

# Security tests
poetry run pytest tests/security

# Performance tests
poetry run pytest tests/performance

# UI tests
poetry run pytest tests/ui
```

### Test with coverage

```
# Run tests with coverage report
poetry run pytest --cov=backend/app --cov-report=term --cov-report=html
```

## Quality Requirements

The tests in this directory ensure the following quality requirements are met:

### Maintainability

- **Line Coverage**: Minimum 80%
- **Code Quality**: Flake8 and Bandit without warnings
- **Mutation Testing**: Using mutmut to find gaps in test coverage

### Reliability

- **Error Recovery**: Tests for system resilience
- **Edge Cases**: Property-based testing with Hypothesis

### Performance

- **Response Times**: 
  - Poll creation ≤500 ms
  - Voting ≤300 ms
  - Results retrieval ≤1 sec
- **Load Testing**: Using Locust to simulate concurrent users

### Security

- **Authentication**: Tests for secure authentication flows
- **Data Validation**: Input validation and sanitization
- **XSS Protection**: Tests for cross-site scripting vulnerabilities
- **SQL Injection**: Tests for SQL injection vulnerabilities
- **Access Control**: Tests for proper access restrictions

## CI/CD Integration

These tests are fully integrated with CI/CD pipeline in GitHub Actions. The pipeline runs all tests on each pull request and merges to the main branch, ensuring code quality is maintained.

## Adding New Tests

When adding new tests, please:

1. Follow the existing directory structure
2. Use appropriate markers: `@pytest.mark.unit`, `@pytest.mark.integration`, etc.
3. Include docstrings that explain the purpose of each test
4. Maintain the AAA pattern (Arrange, Act, Assert)

## Tools Used

- **pytest**: Test runner
- **pytest-cov**: Coverage measurement
- **hypothesis**: Property-based testing
- **mutmut**: Mutation testing
- **locust**: Performance testing
- **selenium**: UI testing
- **bandit**: Security analysis
- **flake8**: Code quality checks 