import json
from pathlib import Path
import tempfile
import unittest
from check_evidence import check
from staging import dataset_names
from preflight import validate


class GuardChecks(unittest.TestCase):
    def test_cleanup_rejects_production_and_other_run(self):
        for dataset in ('production', 'dbt_ci_12_2', 'dbt_ci_12_1; DROP SCHEMA production'):
            with self.assertRaises(ValueError):
                dataset_names(dict(DBT_DATASET=dataset, GITHUB_RUN_ID='12', GITHUB_RUN_ATTEMPT='1'))
        self.assertEqual(dataset_names(dict(DBT_DATASET='dbt_ci_12_1', GITHUB_RUN_ID='12', GITHUB_RUN_ATTEMPT='1')), ('dbt_ci_12_1', 'dbt_ci_12_1_snapshots'))

    def test_evidence_rejects_wrong_revision_attempt_and_failure(self):
        env = dict(GITHUB_SHA='abc', GITHUB_RUN_ID='12', GITHUB_RUN_ATTEMPT='1')
        good = dict(status='success', sha='abc', run_id='12', run_attempt='1')
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'evidence.json'
            path.write_text(json.dumps(good))
            self.assertEqual(check(folder, env), good)
            for key, value in [('sha', 'other'), ('run_attempt', '2'), ('status', 'failure')]:
                path.write_text(json.dumps(dict(good, **{key: value})))
                with self.assertRaises(ValueError):
                    check(folder, env)

    def test_preflight_requires_explicit_cloud_settings(self):
        with self.assertRaises(ValueError):
            validate('production', {})


if __name__ == '__main__':
    unittest.main(verbosity=2)
