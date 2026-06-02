# 議事録

## ディレクトリ構成

```
minutes/
  _template/
    YYYY-MM-DD.md     # テンプレート
  会社名/
    YYYY-MM-DD.md     # 各回の議事録
```

## 新規議事録の作成手順

1. 対象会社のフォルダがなければ作成する
2. `_template/YYYY-MM-DD.md` を対象フォルダにコピーし、日付にリネームする
3. テンプレートの内容を埋める

```bash
# 例：株式会社Aの2026-06-02分を作成
mkdir -p minutes/株式会社A
cp minutes/_template/YYYY-MM-DD.md minutes/株式会社A/2026-06-02.md
```
