import logging

def export_data(**kwargs):
    logging.info("Starting export_data function")
    session = settings.Session()
    
    for query, table_name in OBJECTS_TO_EXPORT:
        try:
            logging.info(f"Executing query for {table_name}")
            result = session.execute(text(query))
            logging.info(f"Query executed successfully for {table_name}, streaming to S3")
            stream_to_S3_fn(result, table_name)
            logging.info(f"Data streamed to S3 successfully for {table_name}")
        except Exception as e:
            logging.error(f"Error exporting data for {table_name}: {e}")
            raise

    session.close()
    logging.info("export_data function completed successfully")
    return "OK"