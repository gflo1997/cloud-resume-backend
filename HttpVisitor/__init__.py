import logging
import json
import os
from azure.data.tables import TableClient
import azure.functions as func

# Database configuration
# The connection string is automatically read from the AzureWebJobsStorage setting
CONNECTION_STRING = os.environ["AzureWebJobsStorage"]
TABLE_NAME = "visits"
PARTITION_KEY = "counter"
ROW_KEY = "uniqueId"

# Initialize TableClient
# Note: Doing this outside main is a common pattern for function performance.
try:
    table_client = TableClient.from_connection_string(
        conn_str=CONNECTION_STRING,
        table_name=TABLE_NAME
    )
except Exception as e:
    logging.error(f"Failed to initialize TableClient: {e}")
    table_client = None

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # 1. CORS Headers for success (even if database fails, CORS must be sent)
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "https://mango-rock-0b7c7e40f.3.azurestaticapps.net", # Securely limits access to your website
        "Access-Control-Allow-Methods": "GET"
    }
    
    if table_client is None:
        return func.HttpResponse(
             "Database client not initialized.",
             status_code=500,
             headers=headers
        )

    try:
        # 2. Retrieve the existing counter entity
        try:
            entity = table_client.get_entity(PARTITION_KEY, ROW_KEY)
            current_count = int(entity['count'])
        except Exception:
            # If entity is not found (first run), start at 0
            current_count = 0

        # 3. Increment the count
        new_count = current_count + 1
        
        # 4. Update the entity with the new count
        updated_entity = {
            'PartitionKey': PARTITION_KEY,
            'RowKey': ROW_KEY,
            'count': new_count
        }
        table_client.upsert_entity(updated_entity)

        # 5. Prepare the final JSON response
        response_data = {
            "count": new_count
        }

        return func.HttpResponse(
            json.dumps(response_data),
            headers=headers,
            status_code=200
        )

    except Exception as e:
        logging.error(f"Database read/write failed: {e}")
        return func.HttpResponse(
             "Database update failed.",
             status_code=500,
             headers=headers
        )
