from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.decorators import dag, task
from airflow.models.baseoperator import chain, cross_downstream

from datetime import datetime, timedelta

default_args = {
    'retries': 5,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email_on_retry': True,
    'email': 'admin@astro.com'
}


def _downloading_data(ti, **kwargs):
    with open('/tmp/my_file.txt', 'w') as f:
        f.write('my_data')
    ti.xcom_push(key='my_key', value=43)


def _checking_data(ti):
    my_xcom = ti.xcom_pull(key='my_key', task_ids=['downloading_data'])
    print(my_xcom)


def _failure(context):
    print('I failed, on callback failure')


with DAG(dag_id='simple_dag', default_args=default_args, schedule_interval="@daily",  # timedelta(days=1),
         start_date=days_ago(3), catchup=True) as dag:

    downloading_data = PythonOperator(
        task_id='downloading_data',
        python_callable=_downloading_data
    )

    checking_data = PythonOperator(
        task_id='checking_data',
        python_callable=_checking_data
    )

    waiting_for_data = FileSensor(
        task_id='waiting_for_data',
        fs_conn_id='fs_default',
        filepath='/tmp/my_file.txt'
    )

    processing_data = BashOperator(
        task_id='processing_data',
        bash_command='exit 0',
        on_failure_callback=_failure
    )

    # downloading_data.set_downstream(waiting_for_data)
    # waiting_for_data.set_downstream(processing_data)

    # processing_data.set_upstream(waiting_for_data)
    # waiting_for_data.set_upstream(downloading_data)

    # cross_downstream([downloading_data, checking_data],
    #                  [waiting_for_data, processing_data])

    chain(downloading_data, checking_data, waiting_for_data, processing_data)
