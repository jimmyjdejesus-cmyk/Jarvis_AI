
Copyright (c) 2025 Jimmy De Jesus (Bravetto)

Licensed under the Creative Commons Attribution 4.0 International (CC BY 4.0).
See https://creativecommons.org/licenses/by/4.0/ for license terms.

# Contract Testing Suite

This directory contains comprehensive contract-based testing for the AdaptiveMind AI API, including schema validation, performance testing, integration testing, and monitoring capabilities.

## Overview

The contract testing suite ensures API reliability through:

- **Schema Validation**: Validates all API responses against OpenAPI specifications
- **Performance Testing**: Monitors response times, throughput, and detects performance regressions
- **Integration Testing**: Tests end-to-end workflows, database state, and external dependencies
- **Error Handling**: Validates proper error responses and recovery mechanisms
- **Contract Monitoring**: Provides continuous monitoring of API contract compliance

## Test Modules

### 1. API Contract Testing (`test_api_contracts.py`)
- JSON Schema validation for all API responses
- Business rule validation
- Property-based testing
- Error scenario testing
- Contract violation reporting

### 2. Performance Contract Testing (`test_performance_contracts.py`)
- Response time validation against thresholds
- Throughput and latency testing
- Performance regression detection
- Load testing capabilities
- Baseline performance tracking

### 3. Integration Contract Testing (`test_integration_contracts.py`)
- End-to-end workflow testing
- Database state validation
- External dependency mocking
- Concurrent request handling
- Error handling and recovery testing

### 4. Configuration (`conftest.py`)
- Pytest fixtures for contract testing
- Test data and endpoint definitions
- Performance thresholds configuration
- Error scenario definitions

## Quick Start

### Run All Contract Tests
```bash
# Run all contract tests
python -m pytest tests/contract_tests/ -v

# Run specific test categories
python -m pytest tests/contract_tests/test_api_contracts.py -v
python -m pytest tests/contract_tests/test_performance_contracts.py -v
python -m pytest tests/contract_tests/test_integration_contracts.py -v
```

### Run Performance Tests
```bash
# Run performance tests and generate baseline
python tests/contract_tests/test_performance_contracts.py

# Run with custom configuration
export TEST_BASE_URL="http://your-api:8000"
export TEST_API_KEY="your-api-key"
python tests/contract_tests/test_performance_contracts.py
```

### Run Integration Tests
```bash
# Run integration tests
python tests/contract_tests/test_integration_contracts.py

# Run with database validation
export DATABASE_URL="postgresql://..."
python tests/contract_tests/test_integration_contracts.py
```

## Test Configuration

### Environment Variables
- `TEST_BASE_URL`: API base URL (default: http://127.0.0.1:8000)
- `TEST_API_KEY`: API authentication key
- `DATABASE_URL`: Database connection string for state validation

### Performance Thresholds
Configure performance thresholds in `conftest.py`:

```python
performance_thresholds = {
    'health': {'max_response_time_ms': 100},
    'models': {'max_response_time_ms': 200},
    'chat': {'max_response_time_ms': 5000},
    'agents': {'max_response_time_ms': 1000},
    'monitoring': {'max_response_time_ms': 500}
}
```

## Test Coverage

### Endpoints Covered
- `/health` - Health check endpoint
- `/models` - List available models
- `/chat` - Chat completion
- `/chat/stream` - Streaming chat completion
- `/agents` - Agent management
- `/agents/execute` - Agent execution
- `/memory/*` - Memory management
- `/workflows/*` - Workflow operations
- `/security/*` - Security validation
- `/monitoring/*` - Monitoring endpoints
- `/jobs/*` - Job processing

### Test Scenarios
1. **Happy Path**: Normal operation with valid requests
2. **Error Handling**: Invalid requests, authentication failures
3. **Performance**: Response time, throughput, concurrent handling
4. **Integration**: End-to-end workflows, database state
5. **Regression**: Performance regression detection
6. **Load**: Concurrent request handling

## Contract Validation

### Schema Validation
All API responses are validated against OpenAPI 3.0 specifications:
- Required field validation
- Data type validation
- Enum value validation
- Format validation (dates, UUIDs, etc.)

### Business Rule Validation
Endpoint-specific business rules:
- Health responses must include `status` and `timestamp`
- Chat responses must include `content` and `model`
- Job responses must include `job_id` and `status`

### Performance Contracts
- Response time thresholds per endpoint type
- Minimum success rates
- Throughput requirements
- P95/P99 latency requirements

## Reports and Monitoring

### Test Reports
- Comprehensive JSON reports generated for all test runs
- Performance baselines for regression detection
- Integration test summaries with workflow validation results

### Contract Violations
- Real-time contract violation detection
- Severity levels (CRITICAL, HIGH, MEDIUM, LOW)
- Automated reporting and alerting

### Performance Monitoring
- Response time trend analysis
- Throughput monitoring
- Error rate tracking
- Performance regression alerts

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Contract Testing
on: [push, pull_request]

jobs:
  contract-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run contract tests
        run: python -m pytest tests/contract_tests/ -v --json-report --json-report-file=contract-test-results.json
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: contract-test-results
          path: contract-test-results.json
```

### Contract Validation Gates
- Pre-deployment contract validation
- Performance regression blocking
- Schema change detection
- Breaking change identification

## Extending Tests

### Adding New Endpoints
1. Add endpoint definition to `conftest.py` test_endpoints fixture
2. Add schema validation rules to appropriate test module
3. Add performance thresholds if needed
4. Add integration test scenarios

### Custom Business Rules
Extend the `_validate_business_rules` method in `APIContractTester` to add endpoint-specific validation logic.

### Performance Monitoring
Add new performance thresholds in `conftest.py` and implement monitoring logic in `PerformanceContractTester`.

## Troubleshooting

### Common Issues
1. **Schema validation failures**: Check OpenAPI specification alignment
2. **Performance regressions**: Update baseline or investigate performance issues
3. **Integration test failures**: Verify external service availability
4. **Authentication errors**: Check API key configuration

### Debug Mode
Enable verbose logging:
```bash
export CONTRACT_TEST_DEBUG=1
python -m pytest tests/contract_tests/ -v -s
```

## Best Practices

1. **Regular Baseline Updates**: Update performance baselines after major releases
2. **Comprehensive Coverage**: Ensure all endpoints have contract tests
3. **Continuous Monitoring**: Run contract tests in CI/CD pipeline
4. **Documentation Sync**: Keep OpenAPI spec synchronized with implementation
5. **Regression Prevention**: Use contract tests to prevent breaking changes

## Contributing

When adding new contract tests:
1. Follow the existing pattern in the test modules
2. Add appropriate fixtures in `conftest.py`
3. Include both positive and negative test cases
4. Add performance thresholds if applicable
5. Update documentation

For questions or issues, please refer to the main project documentation or create an issue in the project repository.
