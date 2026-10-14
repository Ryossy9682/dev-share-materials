"""Isolated BigQuery fixtures; never permit cleanup of a production dataset."""
import json
import os
from pathlib import Path
import re
import shutil
import sys
from preflight import validate

ROOT = Path(__file__).resolve().parents[1]


def dataset_names(env):
    base = env.get('DBT_DATASET', '')
    expected = f"dbt_ci_{env.get('GITHUB_RUN_ID')}_{env.get('GITHUB_RUN_ATTEMPT')}"
    if not re.fullmatch(r'dbt_ci_\d+_\d+', base) or base != expected:
        raise ValueError('Refusing to operate outside this run CI datasets')
    return base, base + '_snapshots'


def main(command):
    validate('staging', os.environ)
    datasets = dataset_names(os.environ)
    if command == 'phase2':
        for name in ('raw_orders', 'raw_customers', 'raw_events'):
            shutil.copyfile(ROOT / 'fixtures' / 'phase2' / f'{name}.csv',
                            ROOT / 'projects' / 'patterns' / 'seeds' / f'{name}.csv')
        return
    from google.cloud import bigquery
    project, location = os.environ['DBT_PROJECT'], os.environ['DBT_LOCATION']
    client = bigquery.Client(project=project, location=location)
    if command == 'prepare':
        for name in datasets:
            dataset = bigquery.Dataset(f'{project}.{name}')
            dataset.location = location
            dataset.default_table_expiration_ms = 86400000
            dataset.labels = {'purpose': 'github-ci', 'run_id': os.environ['GITHUB_RUN_ID']}
            client.create_dataset(dataset, exists_ok=False)
    elif command == 'cleanup':
        for name in datasets:
            client.delete_dataset(f'{project}.{name}', delete_contents=True, not_found_ok=True)
    elif command == 'verify':
        def scalar(table, expression):
            query = f'SELECT {expression} AS result FROM `{project}.{table}`'
            config = bigquery.QueryJobConfig(maximum_bytes_billed=1000000000)
            return float(next(iter(client.query(query, job_config=config, location=location).result(timeout=300))).result)
        base = datasets[0]
        checks = {
            'full_rebuild_paid': (scalar(base + '.mart_sales_daily', 'SUM(net_revenue)'), 349),
            'merge_paid_with_known_delete_gap': (scalar(base + '.p05_orders_merge', "SUM(IF(status = 'paid', net_amount, 0))"), 469),
            'overwrite_paid': (scalar(base + '.p06_orders_insert_overwrite', "SUM(IF(status = 'paid', net_amount, 0))"), 349),
            'event_count': (scalar(base + '.p04_events_incremental', 'COUNT(*)'), 4),
            'active_customers': (scalar(datasets[1] + '.snap_customers', 'COUNTIF(dbt_valid_to IS NULL)'), 3),
        }
        if any(actual != expected for actual, expected in checks.values()):
            raise AssertionError(checks)
        evidence = dict(status='success', sha=os.environ['GITHUB_SHA'],
                        run_id=os.environ['GITHUB_RUN_ID'], run_attempt=os.environ['GITHUB_RUN_ATTEMPT'],
                        checks={k: {'actual': a, 'expected': e} for k, (a, e) in checks.items()})
        output = ROOT / 'ci-evidence' / 'evidence.json'
        output.parent.mkdir(exist_ok=True)
        output.write_text(json.dumps(evidence, indent=2) + '\n')
        print(json.dumps(evidence['checks'], indent=2))
    else:
        raise ValueError('Unknown command')


if __name__ == '__main__':
    main(sys.argv[1])
