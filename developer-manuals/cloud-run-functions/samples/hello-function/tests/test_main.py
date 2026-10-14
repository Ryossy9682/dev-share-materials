"""HTTPステータス、JSON、入力境界をFunctions Framework経由で検証します。"""
from pathlib import Path
import unittest
import functions_framework


class HelloTests(unittest.TestCase):
    """マニュアルの関数に対する受入テストです。"""

    @classmethod
    def setUpClass(cls):
        """実際の入口関数を読み込み、HTTPテストクライアントを作ります。"""
        app = functions_framework.create_app(
            target="hello", source=str(Path(__file__).resolve().parents[1] / "main.py")
        )
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_named_greeting(self):
        """名前付きGETの成功レスポンスを確認します。"""
        response = self.client.get("/", query_string={"name": "Developer"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Hello, Developer!"})

    def test_default_and_blank(self):
        """未指定、空文字、空白だけの入力が既定値になることを確認します。"""
        for query in ({}, {"name": ""}, {"name": "   "}):
            with self.subTest(query=query):
                response = self.client.get("/", query_string=query)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json, {"message": "Hello, World!"})

    def test_length_boundary(self):
        """50文字は許可し、51文字は400を返す境界を確認します。"""
        self.assertEqual(self.client.get("/", query_string={"name": "x" * 50}).status_code, 200)
        response = self.client.get("/", query_string={"name": "x" * 51})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "name_too_long"})

    def test_method_rejection(self):
        """POSTが405となり、許可メソッドがGETと通知されることを確認します。"""
        response = self.client.post("/")
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.json, {"error": "method_not_allowed"})
        self.assertEqual(response.headers["Allow"], "GET")

    def test_unicode_and_trim(self):
        """日本語の入力と前後の空白除去を確認します。"""
        response = self.client.get("/", query_string={"name": " よっしー "})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Hello, よっしー!"})


if __name__ == "__main__":
    unittest.main()
