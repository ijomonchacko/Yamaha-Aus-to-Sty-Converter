import json
import subprocess

def handler(request):
    try:
        result = subprocess.run(['python', 'api/main.py'], capture_output=True, text=True)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"output": result.stdout, "error": result.stderr})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
