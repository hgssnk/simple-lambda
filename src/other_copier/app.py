"""PDF 以外のファイルを Other Bucket へコピーする Lambda ハンドラー。

SQS 経由（SNS からの RawMessageDelivery）で S3 イベント通知を受け取り、
アップロードされたオブジェクトを DEST_BUCKET_NAME 環境変数のバケットへコピーする。
拡張子による絞り込みは template.yaml の Lambda イベントソースマッピングの
FilterCriteria で行っているため、ここでは判定しない。
"""

import json
import logging
import os
import urllib.parse

import boto3

# ログレベル
LOG_LEVEL = logging.INFO

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

# s3クラウイアントの作成
s3 = boto3.client("s3")

# 環境変数の取得
DEST_BUCKET_NAME = os.environ["DEST_BUCKET_NAME"]


# Lambda ハンドラー
def handler(event, context):
    for record in event["Records"]:
        try:
            copy_s3_object(record)
        except Exception:
            # 例外をログに記録し、再試行は SQS の可視性タイムアウト等の設定に任せる
            logger.exception("Failed to copy object for record: %s", record)
            raise


# SQS メッセージ（RawMessageDelivery された S3 イベント通知）を処理する関数
def copy_s3_object(record):
    # S3 の Records は仕様上複数件を含みうるが、実運用ではほぼ 1 件のため、
    # 先頭の 1 件だけを処理する簡易実装にしている。
    body = json.loads(record["body"])
    s3_record = body["Records"][0]
    source_bucket = s3_record["s3"]["bucket"]["name"]
    source_key = urllib.parse.unquote_plus(s3_record["s3"]["object"]["key"])

    logger.info(
        "Copying s3://%s/%s to s3://%s/%s",
        source_bucket,
        source_key,
        DEST_BUCKET_NAME,
        source_key,
    )
    s3.copy_object(
        Bucket=DEST_BUCKET_NAME,
        Key=source_key,
        CopySource={"Bucket": source_bucket, "Key": source_key},
    )
