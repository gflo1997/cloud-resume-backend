import logging
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HTTP trigger function processed a request.')

    count = 1

    return func.HttpResponse(
        json.dumps({"count": count}),
        mimetype="application/json",
        status_code=200
    )
