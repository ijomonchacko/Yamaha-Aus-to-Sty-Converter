import json
from api.main import main  # Ensure 'main.py' has a callable function

def handler(request):
    try:
        output = main()  # Call main function directly
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"output": output})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
