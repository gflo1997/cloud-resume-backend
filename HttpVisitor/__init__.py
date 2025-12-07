import logging
import json

import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Diagnostic HttpVisitor hit")

    # Try to import the table package at runtime
    try:
        from azure.data.tables import TableServiceClient, UpdateMode
        msg = "import_ok"
    except Exception as e:
        msg = f"import_failed: {repr(e)}"

    return func.HttpResponse(
        json.dumps({"result": msg}),
        mimetype="application/json",
        status_code=200,
    )
