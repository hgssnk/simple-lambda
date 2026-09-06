"""固定レスポンスを返すLambda関数のサンプルコードです。"""

import logging

# ログレベル
LOG_LEVEL = logging.INFO

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)


# Lamndaハンドラー
def handler(event, context):
    try:
        return hello_world_response()
    except Exception:
        # 例外をログに記録し、再試行は外部設定（Lambda設定やSQS等）に任せる
        logger.exception("Lambda execution failed; re-raising for retry.")
        raise


# 固定レスポンスを返す関数
def hello_world_response():
    return {
        "statusCode": 200,
        "body": "Hello, World!",
    }
