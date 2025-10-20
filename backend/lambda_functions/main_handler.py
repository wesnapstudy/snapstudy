"""
Main Lambda handler for SnapStudy API.

This is the primary Lambda function that handles all API requests through API Gateway.
"""

import json
import logging
import os
import sys
from typing import Dict, Any

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mangum import Mangum
try:
    from src.api.main import app
except ImportError:
    # Fallback for different path structures
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from src.api.main import app

# Configure logging for Lambda
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create the Mangum handler
handler = Mangum(app, lifespan="off")

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler function.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    try:
        # Log the incoming event (excluding sensitive data)
        logger.info(f"Processing request: {event.get('httpMethod', 'UNKNOWN')} {event.get('path', 'UNKNOWN')}")
        
        # Add request context to the event
        if 'requestContext' in event:
            event['requestContext']['functionName'] = context.function_name
            event['requestContext']['functionVersion'] = context.function_version
            event['requestContext']['awsRequestId'] = context.aws_request_id
        
        # Process the request through Mangum
        response = handler(event, context)
        
        # Log successful response
        status_code = response.get('statusCode', 500)
        logger.info(f"Request completed with status: {status_code}")
        
        return response
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}", exc_info=True)
        
        # Return a generic error response
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'An unexpected error occurred',
                    'timestamp': '2024-01-01T00:00:00Z',
                    'request_id': context.aws_request_id if context else 'unknown'
                }
            })
        }

# For local testing
if __name__ == "__main__":
    # Test event for local development
    test_event = {
        "httpMethod": "GET",
        "path": "/health",
        "headers": {},
        "queryStringParameters": None,
        "body": None,
        "requestContext": {
            "requestId": "test-request-id"
        }
    }
    
    class MockContext:
        function_name = "snapstudy-api-local"
        function_version = "$LATEST"
        aws_request_id = "test-request-id"
    
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))