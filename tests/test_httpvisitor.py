import os
import json
from unittest.mock import patch, MagicMock

import azure.functions as func
from HttpVisitor import __init__ as httpvisitor


def _set_connection_string():
    # function will throw if this is missing
    os.environ["AzureWebJobsStorage"] = "UseDevelopmentStorage=true"


@patch("HttpVisitor.__init__.TableServiceClient")
def test_existing_entity_is_incremented(mock_table_service_client):
    _set_connection_string()

    # arrange fake table and entity
    mock_table_client = MagicMock()
    mock_table_service_client.from_connection_string.return_value.get_table_client.return_value = mock_table_client

    existing_entity = {
        "PartitionKey": "counter",
        "RowKey": "1",
        "count": 5,
    }
    mock_table_client.get_entity.return_value = existing_entity

    # act
    req = func.HttpRequest(
        method="GET",
        url="http://localhost/api/HttpVisitor",
        body=b"",
        params={},
        headers={},
    )
    resp = httpvisitor.main(req)

    # assert response
    assert resp.status_code == 200
    body = json.loads(resp.get_body())
    assert body["count"] == 6

    # assert entity was updated in storage
    mock_table_client.update_entity.assert_called_once()
    updated_entity = mock_table_client.update_entity.call_args.kwargs["entity"]
    assert updated_entity["count"] == 6


@patch("HttpVisitor.__init__.TableServiceClient")
def test_missing_entity_creates_new_row(mock_table_service_client):
    _set_connection_string()

    mock_table_client = MagicMock()
    mock_table_service_client.from_connection_string.return_value.get_table_client.return_value = mock_table_client

    # simulate missing entity
    mock_table_client.get_entity.side_effect = Exception("not found")

    req = func.HttpRequest(
        method="GET",
        url="http://localhost/api/HttpVisitor",
        body=b"",
        params={},
        headers={},
    )
    resp = httpvisitor.main(req)

    assert resp.status_code == 200
    body = json.loads(resp.get_body())
    assert body["count"] == 1

    # verify create_entity called once with count 1
    mock_table_client.create_entity.assert_called_once()
    created_entity = mock_table_client.create_entity.call_args.kwargs["entity"]
    assert created_entity["PartitionKey"] == "counter"
    assert created_entity["RowKey"] == "1"
    assert created_entity["count"] == 1


def test_missing_connection_string_returns_error():
    # clear connection string so function fails fast
    if "AzureWebJobsStorage" in os.environ:
        del os.environ["AzureWebJobsStorage"]

    req = func.HttpRequest(
        method="GET",
        url="http://localhost/api/HttpVisitor",
        body=b"",
        params={},
        headers={},
    )
    resp = httpvisitor.main(req)

    assert resp.status_code == 500
    body = json.loads(resp.get_body())
    assert "AzureWebJobsStorage" in body["error"]
