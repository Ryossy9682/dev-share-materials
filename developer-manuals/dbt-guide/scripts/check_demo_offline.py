"""架空CSVとモデルのSELECTをローカルで検算します。BigQueryの実行検証ではありません。"""
from pathlib import Path
import unittest
import duckdb
import sqlglot
from jinja2 import Environment, StrictUndefined

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "projects" / "patterns"


class DemoChecks(unittest.TestCase):
    """金額、状態、粒度、更新と物理削除の違いを確認します。"""

    def setUp(self):
        self.db = duckdb.connect()
        self.load_fixture("phase1")
        self.db.execute("create table status_labels as select * from read_csv_auto(?)", [str(PROJECT / "seeds/status_labels.csv")])
        self.env = Environment(undefined=StrictUndefined, extensions=["jinja2.ext.do"])
        self.build_base()
        for name in ("p03_orders_enriched_table", "p03_sales_by_segment", "p04_events_incremental", "p05_orders_merge", "p06_orders_insert_overwrite", "p08_seed_lookup", "p09_wide_bi_table"):
            self.make_table(name)

    def tearDown(self):
        self.db.close()

    def load_fixture(self, phase):
        for name in ("raw_orders", "raw_customers", "raw_events"):
            self.db.execute(f"create or replace table {name} as select * from read_csv_auto(?)", [str(ROOT / "fixtures" / phase / f"{name}.csv")])

    def render(self, name, incremental=False):
        path = next(PROJECT.glob(f"models/**/{name}.sql"))
        macro = (PROJECT / "macros/net_amount.sql").read_text(encoding="utf-8")
        variables = {"merge_lookback_days": 3, "rebuild_dates": ["2026-10-01", "2026-10-02", "2026-10-03"]}
        context = dict(ref=lambda value: value, source=lambda group, value: value,
                       config=lambda *args, **kwargs: "", is_incremental=lambda: incremental,
                       this=name, var=lambda key, default=None: variables.get(key, default))
        rendered = self.env.from_string(macro + "\n" + path.read_text(encoding="utf-8")).render(**context)
        tree = sqlglot.parse_one(rendered, read="bigquery")
        # 固定版SQLGlotのTIMESTAMP_SUB出力を、DuckDBの等価なINTERVAL演算へ変換します。
        def adapt_timestamp_sub(node):
            if isinstance(node, sqlglot.exp.TimestampSub):
                return sqlglot.exp.Sub(
                    this=node.this.copy(),
                    expression=sqlglot.exp.Interval(this=node.expression.copy(), unit=node.args["unit"].copy()),
                )
            return node
        return tree.transform(adapt_timestamp_sub).sql(dialect="duckdb")

    def make_table(self, name):
        self.db.execute(f"create or replace table {name} as {self.render(name)}")

    def build_base(self):
        for name in ("stg_orders", "stg_customers", "stg_events", "int_paid_orders_ephemeral", "mart_sales_daily", "p01_sales_view"):
            self.make_table(name)

    def total(self, table, column="net_revenue", where=""):
        return float(self.db.execute(f"select sum({column}) from {table} {where}").fetchone()[0])

    def test_phase1_amounts_and_grain(self):
        """基準の入金済み売上680、4注文、3日分を確認します。"""
        self.assertEqual(self.total("mart_sales_daily"), 680.0)
        self.assertEqual(self.db.execute("select sum(paid_order_count) from mart_sales_daily").fetchone()[0], 4)
        self.assertEqual(self.db.execute("select count(*) from mart_sales_daily").fetchone()[0], 3)
        self.assertEqual(self.total("p09_wide_bi_table", "net_amount"), 680.0)

    def test_lookup_does_not_duplicate_orders(self):
        """seed結合で注文が増殖しないことと、日本語ラベルを確認します。"""
        self.assertEqual(self.db.execute("select count(*) from p08_seed_lookup").fetchone()[0], 6)
        self.assertEqual(self.db.execute("select status_label from p08_seed_lookup where order_id=1").fetchone()[0], "入金済み")

    def test_phase2_full_rebuild(self):
        """全件再作成は修正・キャンセル・物理削除を反映し、349になることを確認します。"""
        self.load_fixture("phase2")
        self.build_base()
        self.assertEqual(self.total("mart_sales_daily"), 349.0)
        self.assertEqual(self.db.execute("select sum(paid_order_count) from mart_sales_daily").fetchone()[0], 3)

    def test_merge_selection_and_physical_delete_gap(self):
        """更新対象SELECTを検算し、upsertだけでは物理削除が残ることを示します。"""
        self.load_fixture("phase2")
        self.build_base()
        self.db.execute(f"create table incoming as {self.render('p05_orders_merge', incremental=True)}")
        self.db.execute("delete from p05_orders_merge where order_id in (select order_id from incoming)")
        self.db.execute("insert into p05_orders_merge select * from incoming")
        self.assertEqual(self.total("p05_orders_merge", "net_amount", "where status='paid'"), 469.0)
        self.assertEqual(self.db.execute("select count(*) from p05_orders_merge where order_id=6").fetchone()[0], 1)
        self.assertNotEqual(self.total("p05_orders_merge", "net_amount", "where status='paid'"), self.total("mart_sales_daily"))

    def test_partition_replacement_including_empty_partition(self):
        """対象3日を全置換すると、空になった10/3の過去行も消えることを確認します。"""
        self.load_fixture("phase2")
        self.db.execute("delete from raw_orders where order_date='2026-10-03'")
        self.build_base()
        self.db.execute(f"create table incoming as {self.render('p06_orders_insert_overwrite', incremental=True)}")
        self.db.execute("delete from p06_orders_insert_overwrite where order_date in ('2026-10-01','2026-10-02','2026-10-03')")
        self.db.execute("insert into p06_orders_insert_overwrite select * from incoming")
        self.assertEqual(self.total("p06_orders_insert_overwrite", "net_amount", "where status='paid'"), 349.0)
        self.assertEqual(self.db.execute("select count(*) from p06_orders_insert_overwrite where order_id=6").fetchone()[0], 0)
        self.assertEqual(self.db.execute("select count(*) from p06_orders_insert_overwrite where order_date='2026-10-03'").fetchone()[0], 0)

    def test_repeated_event_run_is_empty(self):
        """同じ不変イベントを再実行しても、新規対象SELECTは0件になることを確認します。"""
        self.assertEqual(self.db.execute(self.render("p04_events_incremental", incremental=True)).fetchall(), [])
        self.load_fixture("phase2")
        self.build_base()
        self.assertEqual([r[0] for r in self.db.execute(self.render("p04_events_incremental", incremental=True)).fetchall()], ["e4"])

    def test_late_update_outside_lookback(self):
        """ウォーターマークより古い遅延到着はlookbackで拾えないことを示します。"""
        self.db.execute("insert into raw_orders values (7,101,'2026-09-01',500,0,'paid','2026-09-01 00:00:00+00:00')")
        self.build_base()
        selected = self.db.execute(self.render("p05_orders_merge", incremental=True)).fetchall()
        self.assertNotIn(7, [row[0] for row in selected])
        self.assertEqual(self.total("mart_sales_daily"), 1180.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
