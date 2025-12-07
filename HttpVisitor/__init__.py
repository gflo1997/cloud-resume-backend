import logging
import json
import os

import azure.functions as func
from azure.data.tables import TableServiceClient, UpdateMode


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("HTTP trigger function processed a request for visitor count")

    try:
        # get connection string from app setting
        connection_string = os.getenv("AzureWebJobsStorage")
        if not connection_string:
            raise ValueError("AzureWebJobsStorage setting is missing or empty")

        table_name = "VisitorCounter"

        # create table client
        table_service = TableServiceClient.from_connection_string(
            conn_str=connection_string
        )
        table_client = table_service.get_table_client(table_name=table_name)

        try:
            # get existing entity
            entity = table_client.get_entity(
                partition_key="counter",
                row_key="1",
            )

            current_count = int(entity.get("count", 0))
            new_count = current_count + 1
            entity["count"] = new_count

            table_client.update_entity(
                entity=entity,
                mode=UpdateMode.REPLACE,
            )

        except Exception:
            # if entity does not exist, create it with count 1
            new_count = 1
            entity = {
                "PartitionKey": "counter",
                "RowKey": "1",
                "count": new_count,
            }
            table_client.create_entity(entity=entity)

        return func.HttpResponse(
            json.dumps({"count": new_count}),
            mimetype="application/json",
            status_code=200,
        )

    except Exception as e:
        logging.exception("Error in visitor counter function")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500,
        )
