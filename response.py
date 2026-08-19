import json

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
}


def json_response(status_code, body=None):
    if body is None:
        serialized = ""
    elif isinstance(body, str):
        serialized = body
    else:
        serialized = json.dumps(body, default=str)

    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": serialized,
    }
