# クラウドファンディング公開中案件 日次トラッキング手順

このドキュメントは、毎日実行される自動トラッキング（Routine）が従う手順です。
人間が読んでも同じ手順で手動更新できます。

## 対象スプレッドシート

- URL: https://docs.google.com/spreadsheets/d/1s6zutqA4q1mbFLw2N_d3LbSvxXOtraFJog4p84v9_LY/edit
- ファイルID: `1s6zutqA4q1mbFLw2N_d3LbSvxXOtraFJog4p84v9_LY`
- 対象タブ: 「CFリスト＆実施者リスト」

## 1. 現在公開中の案件を特定する

Google Drive連携（`mcp__Google_Drive__download_file_content`）で、このファイルを
`exportMimeType: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
としてダウンロードし、base64をデコードして `.xlsx` として保存する。
（`read_file_content` は全タブを1つのテキストに結合してしまい、かつハイパーリンクが失われるため使わないこと）

`openpyxl` で「CFリスト＆実施者リスト」シートを開く。列構成（1行目がヘッダー）:

| 列 | 内容 |
|---|---|
| A | No. |
| B | プロジェクト名 |
| C | PO |
| D | 連絡先 |
| E | きっかけ |
| F | ジャンル |
| G | CAMPFIREカテゴリー |
| H | サイト（CAMPFIRE/GCF/READYFOR等） |
| I | 結果（テキストは「目標：n万円\n結果：n万円\n支援者数：n人」。**このセルにハイパーリンクとしてプロジェクトの実URLが埋め込まれている**。`cell.hyperlink.target` で取得する） |
| J | 期間（例: "2026\n8/5-8/31"。これが公開期間） |

「現在公開中」の判定方法:
- J列の文字列から年・開始日・終了日をパースする（表記ゆれあり: `～` `-` `2026\n8月-翌3/31` `未定` など）。
- 今日の日付が 開始日〜終了日 の範囲内にあるものを「公開中」とする。
- 終了日が翌年にまたがる表記（「翌3/31」等）や「未定」は個別に確認する。
- I列のハイパーリンクが無い行（束案件などURL未登録）は対象外。

## 2. 各URLにアクセスして支援金額・支援者数を取得

`WebFetch` でI列のURLにアクセスし、支援金額（支援額/寄付金額）と支援者数（支援者数/寄付者数）を抽出する。

- CAMPFIRE (`camp-fire.jp`): ページ上部の達成金額・支援者数
- GCF (`furusato-tax.jp/gcf/...`): 寄付金額・寄付者数
- 独自サイト（例: `furusato-sasebo.jp`）: サイトごとに表記が異なるため都度確認。
  - 2026-08-25時点、`furusato-sasebo.jp` はHTTP 403でWebFetch/curlともにブロックされ取得不可だった。継続してブロックされる場合はデータを空欄・note列に理由を記載して記録し、次回also再試行する。

## 3. データを蓄積する

`data/cf_tracking.csv` に1日1行を追記する（同じ日付・同じURLの重複行は追記しない。既にある場合は当日分を最新値で上書き）。

列: `date,row_no,project_name,site,url,period_start,period_end,target_amount,support_amount,supporter_count,note`

- **案件の一意キーは`url`（プロジェクトの実URL）。`row_no`（スプレッドシートA列の番号）は表示用の参考情報に過ぎず、
  新しい案件が上に挿入されると全案件の番号がズレる。実際に2026-08-26、佐世保市の案件がまとまって
  1行から18行に分解された際、既存案件の`row_no`が全てズレたことを確認済み。案件の同一性は必ず`url`で判定すること。**
- 金額は円の整数（カンマなし）。
- 取得できなかった項目は空欄にし、`note` に理由を書く。
- `scripts/build_dashboard.py` も `url`（無ければ`project_name`）でグルーピングして推移を計算する実装になっている。

## 4. ダッシュボードを更新する

`dashboard/cf_dashboard.html` を、更新後の `data/cf_tracking.csv` の内容を埋め込んで再生成し、
Artifactとして同じURLに再publishする（新規publishではなく、既存Artifact URLを`url`パラメータで指定して更新すること）。

- 現在のArtifact URL: `docs/cf-tracking-procedure.md` 末尾の「現在のArtifact URL」欄を参照。
- `scripts/build_dashboard.py` は、CSV内の**最新日付の行に含まれていない案件はダッシュボードに表示しない**
  （スプレッドシートから削除された案件・公開期間が終了した案件を自動的に除外するため）。
  過去データはCSVに残るので、案件が復活すれば自動的にまた表示される。
  2026-08-28、ユーザーの依頼によりこの仕様にした。

## 5. メールで日次サマリーを送信する

`Gmail` コネクタで `info@kita1.jp` 宛に、以下を含む日次サマリーを送信する。

- 対象日
- 公開中の各案件: 前日比の支援金額増減・支援者数増減、目標達成率
- 取得できなかった案件があればその旨

## 6. コミット・プッシュ

`data/cf_tracking.csv` と `dashboard/cf_dashboard.html` の変更を
ブランチ `claude/crowdfunding-support-tracking-u8n8s2` にコミットし、pushする。

---

## 現在のArtifact URL

https://claude.ai/code/artifact/9653ca5c-5dda-43f2-a797-f53b9c7cc2e9

（`Artifact` ツールで `url` パラメータにこのURLを指定して再publishすること。`url` を省略すると別のArtifactが新規作成されてしまうので注意。）

※旧URL（f623651d-16b3-49ae-bf6b-caf8b7e5cbb7）は、共有リンク側が古いバージョンのまま
固定表示される不具合が発生したため2026-08-26に廃止し、上記の新URLに切り替えた。
今後また同様の症状（再publishしても閲覧者側の表示が更新されない）が出た場合は、
別のファイルパスから新規publishしてURLを切り替えること。
