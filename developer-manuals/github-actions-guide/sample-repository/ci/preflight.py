"""Validate explicit environment settings before requesting cloud credentials."""
import os
import re
import sys


def validate(mode, env):
    required = ['DBT_PROJECT', 'DBT_DATASET', 'DBT_LOCATION', 'WIF_PROVIDER', 'RUNTIME_SA']
    if mode == 'production':
        required += ['DBT_RAW_PROJECT', 'DBT_RAW_DATASET']
    if mode not in ('staging', 'production'):
        raise ValueError('Unknown mode')
    missing = [key for key in required if not env.get(key, '').strip()]
    if missing:
        raise ValueError('Missing variables: ' + ', '.join(missing))
    if not re.fullmatch(r'[a-z][a-z0-9-]{4,61}[a-z0-9]', env['DBT_PROJECT']):
        raise ValueError('Invalid project ID')
    for key in ('DBT_DATASET', 'DBT_RAW_DATASET'):
        if env.get(key) and not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]{0,1023}', env[key]):
            raise ValueError('Invalid dataset: ' + key)
    if mode == 'staging' and env['DBT_DATASET'] != f"dbt_ci_{env.get('GITHUB_RUN_ID')}_{env.get('GITHUB_RUN_ATTEMPT')}":
        raise ValueError('Staging dataset must belong to this run')
    if mode == 'production' and env['DBT_DATASET'].startswith('dbt_ci_'):
        raise ValueError('Production cannot target a CI dataset')
    if not re.fullmatch(r'projects/\d+/locations/global/workloadIdentityPools/[^/]+/providers/[^/]+', env['WIF_PROVIDER']):
        raise ValueError('Invalid WIF provider resource')
    if not env['RUNTIME_SA'].endswith('.iam.gserviceaccount.com'):
        raise ValueError('Invalid service account')


if __name__ == '__main__':
    validate(sys.argv[1], os.environ)
    print('Environment settings validated')
