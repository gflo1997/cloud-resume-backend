    except Exception as e:
        logging.exception("Error in visitor counter function")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500,
        )
