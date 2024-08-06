from airflow import DAG, settings
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
from sqlalchemy import text
import csv
from io import StringIO
from smart_open import open
import tempfile
import logging

# Define constants
S3_BUCKET = Variable.get("S3_BUCKET", default_var='your_s3_bucket')
S3_KEY = Variable.get("S3_KEY", default_var='data/migration/2.2.2_to_2.4.3/export/')
dag_id = 'db_export'

# SQL Queries
DAG_RUN_SELECT = "select dag_id, execution_date, state, run_id, external_trigger, '\\x' || encode(conf,'hex') as conf, end_date,start_date, run_type, last_scheduling_decision, dag_hash, creating_job_id, null as queued_at, null as data_interval_start, null as data_interval_end  from dag_run"
TASK_INSTANCE_SELECT = "select ti.task_id, ti.dag_id, ti.start_date, ti.end_date, ti.duration, ti.state, ti.try_number, ti.hostname, ti.unixname, ti.job_id, ti.pool, ti.queue, ti.priority_weight, ti.operator, ti.queued_dttm, ti.pid, ti.max_tries, '\\x' || encode(ti.executor_config,'hex') as executor_config , ti.pool_slots, ti.queued_by_job_id, ti.external_executor_id, null as trigger_id , null as trigger_timeout, null as next_method, null as next_kwargs, r.run_id as run_id from task_instance ti, dag_run r where r.dag_id = ti.dag_id AND r.run_id = ti.run_id"
LOG_SELECT = "select dttm, dag_id, task_id, event, execution_date, owner, extra from log"
TASK_FAIL_SELECT = "select tf.task_id, tf.dag_id, tf.start_date, tf.end_date, tf.duration, -1 as map_index, r.run_id from task_fail tf,  dag_run r where r.dag_id = tf.dag_id AND r.execution_date = tf.execution_date"
JOB_SELECT = "select dag_id,  state, job_type , start_date, end_date, latest_heartbeat, executor_class, hostname, unixname from job"
POOL_SLOTS = "select pool, slots, description from slot_pool where pool != 'default_pool'"

OBJECTS_TO_EXPORT = [
    [DAG_RUN_SELECT, "dag_run"],
    [TASK_INSTANCE_SELECT, "task_instance"],
    [LOG_SELECT, "log"],
    [TASK_FAIL_SELECT, "task_fail"],
    [JOB_SELECT, "job"],
    [POOL_SLOTS, "slot_pool"],
]

def stream_to_S3_fn(result, filename):
    try:
        s3_file = f"s3://{S3_BUCKET}/{S3_KEY}{filename}.csv"
        REC_COUNT = 1000
        
        with tempfile.NamedTemporaryFile() as tmp:
            tp = {'writebuffer': tmp}
            with open(s3_file, 'wb', transport_params=tp) as write_io:
                while True:
                    chunk = result.fetchmany(REC_COUNT)
                    if not chunk:
                        break
                    outfileStr = ""
                    f = StringIO(outfileStr)
                    w = csv.writer(f)
                    w.writerows(chunk)
                    write_io.write(f.getvalue().encode("utf8"))
                write_io.close()
        logging.info(f"Data streamed to S3 successfully for {filename}")
    except Exception as e:
        logging.error(f"Error in stream_to_S3_fn for {filename}: {e}")
        raise

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

with DAG(dag_id=dag_id, schedule_interval=None, catchup=False, start_date=days_ago(1)) as dag:
    export_data_t = PythonOperator(
        task_id="export_data",
        python_callable=export_data,
        provide_context=True
    )