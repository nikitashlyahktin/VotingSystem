# Testing Documentation for Voting System

## Quality Requirements

This project establishes concrete quality requirements in the following areas:

### Maintainability
- **Line Coverage**: Minimum 80% measured with pytest-cov
- **Code Quality**: No warnings from Flake8
- **Security Analysis**: No critical vulnerabilities from Bandit
- **Mutation Testing**: Using mutmut to find gaps in test coverage

### Reliability
- **Error Recovery**: Tests for system resilience under various conditions
- **Edge Cases**: Property-based testing with Hypothesis
- **Clean Shutdown**: Verification that database state remains consistent

### Performance
- **Response Times**:
  - Poll creation ≤500 ms
  - Voting ≤300 ms
  - Results retrieval ≤1 sec
- **Load Testing**: Using Locust to simulate concurrent users (10 users, 2 spawned per second)

### Security
- **Authentication**: Tests for token-based authentication and validation
- **Data Validation**: Input validation and sanitization tests
- **XSS Protection**: Tests for cross-site scripting vulnerability prevention
- **SQL Injection**: Tests for SQL injection vulnerability prevention
- **Access Control**: Tests for proper authorization and permission checks

## Test Structure

The tests are organized into the following categories:

```
tests/
├── conftest.py           # Shared fixtures and configurations
├── unit/                 # Unit tests for individual components
├── integration/          # Tests for API endpoints and component integration
├── performance/          # Load and performance tests using Locust
├── security/             # Security and penetration tests
└── ui/                   # Selenium-based UI tests for frontend
```

## Test Tools

| Tool | Purpose | Integration |
|------|---------|------------|
| pytest | Core testing framework | Direct in CI |
| pytest-cov | Coverage measurement | Direct in CI |
| mutmut | Mutation testing | Direct in CI |
| hypothesis | Property-based testing | Direct in CI |
| locust | Performance testing | Direct in CI |
| selenium | UI testing | Direct in CI |
| bandit | Security analysis | Direct in CI |
| flake8 | Code quality checks | Direct in CI |

## Running Tests

### Running All Tests

```bash
poetry run pytest
```

### Running with Coverage

```bash
poetry run pytest --cov=backend/app --cov-report=term --cov-report=html
```

### Running Specific Test Categories

```bash
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

### Running Performance Tests with Locust

```bash
poetry run locust -f tests/performance/locustfile.py --headless -u 10 -r 2 --run-time 1m --host http://localhost:8000
```

### Running Mutation Tests

```bash
poetry run mutmut run --paths-to-mutate=backend/app/domain
poetry run mutmut results
```

## CI/CD Integration

All tests are integrated into our CI/CD pipeline using GitHub Actions (see `.github/workflows/quality.yml`). The pipeline:

1. Runs Flake8 and Bandit for code quality and security checks
2. Executes unit tests with coverage reporting
3. Runs integration tests if unit tests pass
4. Conducts security tests for vulnerability detection
5. Performs performance testing with Locust
6. Executes UI tests with Selenium
7. Runs mutation testing to identify weak test coverage

## Test Coverage

The project aims for a minimum of 80% line coverage, with a target of 80% for critical modules like authentication and poll management. Coverage is measured using pytest-cov and tracked in CI.

## Mutation Testing

Mutation testing is used to assess the quality of our test suite by introducing small changes (mutations) to the code and verifying that the tests detect these changes. This helps identify areas where test coverage is ineffective.

## Property-Based Testing

Using Hypothesis, we implement property-based tests that generate random inputs to find edge cases that might cause issues in our code, particularly focusing on input validation and security vulnerabilities.

## Security Testing

Our security testing validates that:

1. Authentication tokens are properly validated
2. Input is sanitized to prevent XSS attacks
3. Database queries are parameterized to prevent SQL injection
4. Access control is properly enforced
5. Error messages don't leak sensitive information

## Performance Testing

Performance tests use Locust to simulate real-world usage patterns and ensure the system meets performance requirements. Tests are configured to fail if response times exceed the defined thresholds.

## UI Testing

Selenium tests validate the frontend functionality by simulating user interactions with the web interface, ensuring that user flows like registration, login, poll creation, and voting work correctly.

## Test Documentation

Each test includes clear docstrings that explain:
- The purpose of the test
- What's being tested
- Expected behavior
- Any edge cases being considered

This documentation ensures that developers can understand the tests' intentions and maintain them effectively. 