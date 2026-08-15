"""Google Sheetsに登録された予約を読み、送信時刻を過ぎたものをLINEへ送信する。

GitHub Actionsから数分おきに実行される前提のスクリプト。
二重送信を防ぐため、送信済みの行はスプレッドシート側に「TRUE」を書き戻す。
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone

import gspread
import requests
from google.oauth2.service_account import Credentials

JST = timezone(timedelta(hours=9))
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"

COL_DATETIME = "送信日時"
COL_LINE_ID = "宛先LINE ID"
COL_MESSAGE = "メッセージ内容"
COL_SENT = "送信済み"
COL_RESULT = "送信結果"

DATETIME_FORMATS = ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y/%m/%d %H:%M")


def get_worksheet():
    creds_info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    spreadsheet_id = os.environ["SPREADSHEET_ID"]
    sheet_name = os.environ.get("SHEET_NAME", "送信予約")

    creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(spreadsheet_id).worksheet(sheet_name)


def parse_scheduled_at(value):
    value = value.strip()
    for fmt in DATETIME_FORMATS:
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=JST)
        except ValueError:
            continue
    return None


def send_line_message(token, to, message):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {"to": to, "messages": [{"type": "text", "text": message}]}
    return requests.post(LINE_PUSH_URL, headers=headers, json=payload, timeout=10)


def main():
    token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
    worksheet = get_worksheet()

    header = worksheet.row_values(1)
    for required in (COL_DATETIME, COL_LINE_ID, COL_MESSAGE, COL_SENT, COL_RESULT):
        if required not in header:
            print(f"ヘッダーに列 '{required}' が見つかりません: {header}", file=sys.stderr)
            sys.exit(1)

    sent_col = header.index(COL_SENT) + 1
    result_col = header.index(COL_RESULT) + 1

    records = worksheet.get_all_records()
    now = datetime.now(JST)
    sent_count = 0

    for i, record in enumerate(records, start=2):  # 1行目はヘッダー
        if str(record.get(COL_SENT, "")).strip().upper() == "TRUE":
            continue

        scheduled_at = parse_scheduled_at(str(record.get(COL_DATETIME, "")))
        if scheduled_at is None or scheduled_at > now:
            continue

        line_id = str(record.get(COL_LINE_ID, "")).strip()
        message = str(record.get(COL_MESSAGE, "")).strip()
        if not line_id or not message:
            worksheet.update_cell(i, result_col, "エラー: 宛先LINE IDまたはメッセージ内容が空です")
            continue

        response = send_line_message(token, line_id, message)
        if response.status_code == 200:
            worksheet.update_cell(i, sent_col, "TRUE")
            worksheet.update_cell(
                i, result_col, f"送信成功 {now.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            sent_count += 1
            print(f"row {i}: sent to {line_id}")
        else:
            worksheet.update_cell(
                i, result_col, f"送信失敗({response.status_code}): {response.text[:200]}"
            )
            print(f"row {i}: failed {response.status_code} {response.text}", file=sys.stderr)

    print(f"done: {sent_count} message(s) sent")


if __name__ == "__main__":
    main()
