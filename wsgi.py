"""
WSGI entrypoint for Fly.io (gunicorn).

app.py は import されたとき(__name__ != "__main__") に
scheduler.start() を呼ぶ設計になっているため、
ここで `from app import app` するだけで APScheduler が起動する。

ただし gunicorn を --workers 1 で起動することが前提。
workers >= 2 だと 1分ジョブが多重発火するので、fly.toml / Dockerfile を変更しないこと。
"""

from app import app  # noqa: F401  -- gunicorn が "wsgi:app" で参照する

if __name__ == "__main__":
    # ローカル簡易テスト用（本番は gunicorn 経由）
    app.run(host="0.0.0.0", port=8080)
