# SnapStudy Backend Test Suite

This directory contains comprehensive tests for all SnapStudy backend services and functionality.

## Test Files Overview

### Core Service Tests
- **`test_adaptive_agent.py`** - Tests for the adaptive learning agent and AgentCore integration
- **`test_agentcore_integration.py`** - Tests for Bedrock AgentCore primitives integration
- **`test_ai_services.py`** - Tests for AI/ML services and Bedrock integration
- **`test_analytics_system.py`** - Tests for learning analytics and progress tracking
- **`test_bedrock_retry.py`** - Tests for Bedrock retry logic with exponential backoff

### API and Communication Tests
- **`test_api_endpoints.py`** - Tests for REST API endpoints
- **`test_chat_agent.py`** - Tests for agentic chat and tutoring system
- **`test_chat_agent_mock.py`** - Mocked tests for chat functionality (no AWS required)

### Quiz System Tests
- **`test_quiz_engine.py`** - Tests for intelligent quiz generation and evaluation

## Running Tests

### Prerequisites
1. Ensure you're using the `hackathon-user-01` AWS profile:
   ```bash
   $env:AWS_PROFILE = "hackathon-user-01"
   aws sts get-caller-identity  # Verify identity
   ```

2. Install dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```

### Running Individual Tests

```bash
# Run from the backend directory
cd backend

# Test analytics system
python tests/test_analytics_system.py

# Test quiz engine
python tests/test_quiz_engine.py

# Test chat agent (requires AWS)
python tests/test_chat_agent.py

# Test chat agent (mocked, no AWS required)
python tests/test_chat_agent_mock.py

# Test Bedrock retry logic
python tests/test_bedrock_retry.py

# Test adaptive agent
python tests/test_adaptive_agent.py
```

### Running All Tests

```bash
# Run all tests (from backend directory)
python -m pytest tests/ -v

# Or run them individually
for test in tests/test_*.py; do
    echo "Running $test..."
    python "$test"
done
```

## Test Categories

### 🧪 **Unit Tests**
- Individual service functionality
- Core algorithm testing
- Data processing validation

### 🔗 **Integration Tests**
- AWS service integration
- Database operations
- API endpoint testing

### 🎭 **Mocked Tests**
- Tests that don't require AWS credentials
- Isolated functionality testing
- Development environment friendly

### 📊 **System Tests**
- End-to-end functionality
- Complete workflow testing
- Performance validation

## Test Data

Tests create temporary test data in DynamoDB tables. All test data is automatically cleaned up or uses TTL for automatic expiration.

## AWS Requirements

Most tests require AWS credentials for the `hackathon-user-01` user with permissions for:
- DynamoDB (read/write access to SnapStudy tables)
- Bedrock (model invocation permissions)
- S3 (content bucket access)

## Troubleshooting

### Common Issues

1. **AWS Credentials Error**
   ```bash
   # Verify AWS profile
   aws sts get-caller-identity
   # Should show hackathon-user-01
   ```

2. **Import Errors**
   ```bash
   # Ensure you're running from backend directory
   cd backend
   python tests/test_name.py
   ```

3. **Bedrock Throttling**
   - Tests include retry logic with exponential backoff
   - Some tests may take longer due to rate limiting
   - This is expected behavior

### Test Output

Successful tests will show:
```
✅ All tests passed!
🎉 [Service] functionality is working correctly!
```

Failed tests will show detailed error messages and stack traces for debugging.

## Contributing

When adding new functionality:
1. Create corresponding test files in this directory
2. Follow the naming convention: `test_[service_name].py`
3. Include both success and failure test cases
4. Add documentation for new test files in this README