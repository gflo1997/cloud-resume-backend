This repository contains the backend API powering the visitor counter for my Cloud Resume Challenge.  
It is built using **Azure Functions (Python)** and **Azure Table Storage**, and deployed automatically through GitHub Actions.

## Overview
This backend implements a simple but production-relevant serverless API:

- Accepts an anonymous HTTP GET request.  
- Connects to Azure Table Storage.  
- Reads and increments a visitor count.  
- Persists the updated value.  
- Returns the updated count as JSON.

This demonstrates cloud architecture fundamentals, serverless design, CI CD automation, and operational problem solving.

## Technologies Used
- **Azure Function App (Python 3.12)**  
- **Azure Table Storage**  
- **AzureWebJobsStorage connection string**  
- **Serverless execution model**  
- **GitHub Actions for CI CD**  
- **Package deployment using `.python_packages`**  
- **Logging and error handling**  

## Core Function Logic
The function retrieves the current count, increments it, and writes it back to the table.  
Here is the full working implementation:

```python
import logging
import json
import os

import azure.functions as func
from azure.data.tables import TableServiceClient, UpdateMode

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("HTTP trigger function processed a request for visitor count")

    try:
        connection_string = os.getenv("AzureWebJobsStorage")
        if not connection_string:
            raise ValueError("AzureWebJobsStorage setting is missing or empty")

        table_name = "VisitorCounter"
        table_service = TableServiceClient.from_connection_string(conn_str=connection_string)
        table_client = table_service.get_table_client(table_name=table_name)

        try:
            entity = table_client.get_entity(partition_key="counter", row_key="1")
            current_count = int(entity.get("count", 0))
            new_count = current_count + 1
            entity["count"] = new_count
            table_client.update_entity(entity=entity, mode=UpdateMode.REPLACE)
        except Exception:
            new_count = 1
            entity = {"PartitionKey": "counter", "RowKey": "1", "count": new_count}
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

```

## Deployment Pipeline
Deployment is handled entirely through GitHub Actions:
- Code is checked out.
- Python dependencies are installed into .python_packages.
- The function is zipped and uploaded to Azure.
- Azure Functions automatically restarts with the new code.

This ensures consistency and removes all manual deployment steps.

## Architecture Flow
- Frontend sends a GET request to the Function App.
- Function App executes Python code.
- Counter is read or created in Table Storage.
- The value is incremented and written back.
- Updated count is returned as JSON.

## Live API Endpoint: https://gonzalofloresresumefunction-enave3c6akg5d7dg.centralus-01.azurewebsites.net/api/HttpVisitor

## Repository Structure
- HttpVisitor/
    __init__.py
    function.json
- requirements.txt
- host.json
- .github/workflows/function-deploy.yml

## Related Repository
Frontend (Azure Static Web Apps): https://github.com/gflo1997/cloud-resume-frontend
