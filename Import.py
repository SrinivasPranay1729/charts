from airflow import DAG, settings
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from sqlalchemy import text
import boto3
from airflow.utils.task_group import TaskGroup
import os
import csv
from airflow.models import Variable

# S3 bucket where the exported file are
S3_BUCKET = Variable.get("S3_BUCKET", default_var='your_s3_bucket')
# S3 prefix where the exported file are
S3_KEY = Variable.get("S3_KEY", default_var='data/migration/2.2.2_to_2.4.3/export/')

dag_id = 'db_import'

DAG_RUN_IMPORT = "COPY dag_run(dag_id, execution_date, state, run_id, external_trigger, conf, end_date,start_date, run_type, last_scheduling_decision, dag_hash, creating_job_id, queued_at, data_interval_start, data_interval_end) FROM STDIN WITH (FORMAT CSV, HEADER FALSE)"
TASK_INSTANCE_IMPORT = "COPY task_instance(task_id, dag_id, start_date, end_date, duration, state, try_number, hostname, unixname, job_id, pool, queue, priority_weight, operator, queued_dttm, pid, max_tries, executor_config, pool_slots, queued_by_job_id, external_executor_id, trigger_id , trigger_timeout, next_method, next_kwargs, run_id ) FROM STDIN WITH (FORMAT CSV, HEADER FALSE)"
TASK_FAIL_IMPORT = "COPY task_fail(task_id, dag_id, start_date, end_date, duration, map_index, run_id) FROM STDIN WITH (FORMAT CSV, HEADER FALSE)"
JOB_IMPORT = "COPY JOB(dag_id, state, job_type , start_date, end_date, latest_heartbeat, executor_class, hostname, unixname) FROM STDIN WITH (FORMAT CSV, HEADER FALSE)"
LOG_IMPORT = "COPY log(dttm, dag_id, task_id, event, execution_date, owner, extra) FROM STDIN WITH (FORMAT CSV, HEADER FALSE)"
POOL_SLOTS = "COPY slot_pool(pool, slots, description) FROM STDIN WITH (FORMAT CSV, HEADER FALSE)"

OBJECTS_TO_IMPORT = [
    [DAG_RUN_IMPORT, "dag_run.csv"],
    [LOG_IMPORT, "log.csv"],
    [JOB_IMPORT, "job.csv"],
    [POOL_SLOTS, "slot_pool.csv"]
]

def read_s3(filename):
    """Download the file from S3 and return the local file path."""
    resource = boto3.resource('s3')
    bucket = resource.Bucket(S3_BUCKET)
    tempfile = f"/tmp/{filename}"
    bucket.download_file(S3_KEY + filename, tempfile)
    return tempfile

def load_data(**kwargs):
    """Load data from the CSV file into the database."""
    query = kwargs['query']
    tempfile = read_s3(kwargs['file'])
    conn = settings.engine.raw_connection()
    try:
        with open(tempfile, 'r') as f:
            cursor = conn.cursor()
            cursor.copy_expert(query, f)
            conn.commit()
    except Exception as e:
        print("Exception:", e)
    finally:
        conn.close()
        os.remove(tempfile)

with DAG(dag_id=dag_id, schedule_interval=None, catchup=False, start_date=days_ago(1)) as dag:

    with TaskGroup(group_id='import') as import_t:
        for x in OBJECTS_TO_IMPORT:
            load_task = PythonOperator(
                task_id=x[1],
                python_callable=load_data,
                op_kwargs={'query': x[0], 'file': x[1]},
                provide_context=True
            )

    load_task_instance_t = PythonOperator(
        task_id="load_ti",
        op_kwargs={'query': TASK_INSTANCE_IMPORT, 'file': 'task_instance.csv'},
        provide_context=True,
        python_callable=load_data
    )

    load_task_instance_fail_t = PythonOperator(
        task_id="load_ti_fail",
        op_kwargs={'query': TASK_FAIL_IMPORT, 'file': 'task_fail.csv'},
        provide_context=True,
        python_callable=load_data
    )

    import_t >> load_task_instance_t >> load_task_instance_fail_t
