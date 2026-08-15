# LINE予約送信

Google Sheetsに「いつ・誰に・何を送るか」を登録しておくと、GitHub Actionsが5分おきにシートをチェックし、送信時刻を過ぎた行をLINEへ自動送信する仕組みです。

## 仕組み

1. GitHub Actions（`.github/workflows/line-scheduled-send.yml`）が5分おきに起動
2. `line_scheduler/send_scheduled_messages.py` がGoogle Sheetsを読み取り
3. 「送信日時」が現在時刻（JST）を過ぎていて、まだ「送信済み」でない行を LINE Messaging API で送信
4. 送信できた行はシートの「送信済み」列に `TRUE` を書き戻す（二重送信防止）

## 事前準備

### 1. LINE Messaging APIチャネルを用意する

1. [LINE Developers](https://developers.line.biz/) でMessaging APIチャネル（LINE公式アカウント）を作成
2. チャネル設定画面で **チャネルアクセストークン（長期）** を発行
3. 送信先のLINEユーザー/グループの **ID** を控える
   - 個人：Webhookでメッセージを受け取った際の `source.userId` から取得
   - グループ：グループでBotを招待し、Webhookの `source.groupId` から取得

### 2. Google Sheets用のサービスアカウントを用意する

1. Google Cloudプロジェクトで **Google Sheets API** を有効化
2. サービスアカウントを作成し、JSON形式の鍵を発行
3. 送信予約用のGoogle Sheetsを作成し、サービスアカウントのメールアドレス（`xxxx@xxxx.iam.gserviceaccount.com`）を **編集者として共有**

### 3. スプレッドシートの列を用意する

シート名は既定で `送信予約`（変更する場合は `SHEET_NAME` を設定）。1行目をヘッダーとして以下の列を用意してください（列の順序は自由）。

| 送信日時 | 宛先LINE ID | メッセージ内容 | 送信済み | 送信結果 |
|---|---|---|---|---|
| 2026-08-20 09:00 | U1234567890abcdef... | おはようございます、本日の会議は10時からです。 | | |

- **送信日時**：`YYYY-MM-DD HH:MM`（24時間表記、JST想定）
- **宛先LINE ID**：LINEのuserIdまたはgroupId
- **メッセージ内容**：送信するテキスト
- **送信済み**／**送信結果**：スクリプトが自動で書き込むので空欄のまま用意するだけでOK

### 4. GitHub Secretsを登録する

リポジトリの Settings → Secrets and variables → Actions で以下を登録してください。

| Secret名 | 内容 |
|---|---|
| `LINE_CHANNEL_ACCESS_TOKEN` | LINEのチャネルアクセストークン（長期） |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | サービスアカウントのJSON鍵の中身をそのまま貼り付け |
| `SPREADSHEET_ID` | スプレッドシートのURLに含まれるID（`https://docs.google.com/spreadsheets/d/【ここ】/edit`） |

## 使い方

シートに行を追加するだけです。次回のジョブ実行（最大5分後）で送信時刻を過ぎていれば自動送信されます。

手動で今すぐ実行したい場合は、GitHubの Actions タブから「LINE予約送信」ワークフローを `Run workflow` で起動できます。

## 注意事項

- チェック間隔が5分のため、送信時刻とのずれは最大5分程度発生します
- 「送信済み」列を手動で `TRUE` にすると、その行は以降スキップされます
- LINE Messaging APIの無料枠には月間送信数の上限があります。想定送信数に応じてプランを確認してください
