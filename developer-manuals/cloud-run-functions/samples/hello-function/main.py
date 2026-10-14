import logging
import functions_framework
@functions_framework.http
def hello(request):
    """Return a greeting for a validated GET request."""
    if request.method != "GET":
        return {"error": "method_not_allowed"}, 405, {
            "Allow": "GET"
        }
    name = request.args.get("name", "World").strip()
    if len(name) > 50:
        return {"error": "name_too_long"}, 400
    logging.warning("greeting_request_processed")
    return {"message": f"Hello, {name or 'World'}!"}, 200
