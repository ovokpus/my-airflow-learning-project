from airflow.models import DagBag


def test_nb_dags():
    dag_bag = DagBag(include_examples=False)
    nb = len(dag_bag.dags)
    assert nb == 3, "Wrong number of DAGs found, got {0}, expected 3"
