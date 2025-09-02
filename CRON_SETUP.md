# 確認メール送信 Cron Job セットアップガイド

## 概要

確認メール送信機能をRender環境でCron Jobとして実行するためのセットアップガイドです。

## ファイル構成

- `send_confirmation_emails_cron.py` - 単体実行可能なCron Job用スクリプト
- `scheduler.py` - APScheduler用のタスク定義（ローカル開発用）
- `app.py` - `use_reloader=False` を設定して重複APScheduler起動を防止

## Render Cron Job 設定

### 1. Cron Job の追加

Renderダッシュボードで以下の設定を追加：

```bash
# セミナー確認メール送信 (毎分実行)
*/1 * * * * cd /opt/render/project/src && python3 send_confirmation_emails_cron.py >> /tmp/cron_confirmation_emails.log 2>&1
```

### 2. 設定詳細

- **頻度**: 毎分実行 (`*/1 * * * *`)
- **実行ディレクトリ**: `/opt/render/project/src` (Renderのデフォルト)
- **ログファイル**: `/tmp/cron_confirmation_emails.log`
- **エラーログ**: `2>&1` でエラーもログファイルに出力

### 3. 動作仕様

- セミナー開始の **14-16分前** (15分前の±1分幅) に実行
- `status='attend'` の登録者にのみ確認メールを送信
- 重複送信防止機能付き（セッション内 + 環境間）

## 重複送信防止

### ローカル環境

- `app.py` で `use_reloader=False` を設定
- APSchedulerの重複起動を防止
- `_sent_confirmation_emails` セットによるセッション内重複防止

### 環境間重複防止

- `/tmp/confirmation_emails_sent.txt` ファイルによる日次キャッシュ
- フォーマット: `YYYY-MM-DD:seminar_id_recipient_id`
- 日次自動クリーンアップ機能付き

## ログ確認

### Render環境

```bash
# Cron Job実行ログ
tail -f /tmp/cron_confirmation_emails.log

# アプリケーションログ
# Renderダッシュボードの "Logs" タブから確認
```

### ローカル環境

```bash
# APScheduler実行時
python3 app.py

# Cron Job テスト実行時  
python3 send_confirmation_emails_cron.py
```

## トラブルシューティング

### よくある問題

1. **メール送信エラー**
   - `config.py` のSMTP設定を確認
   - Gmail App Passwordの設定確認

2. **データベース接続エラー**
   - `DATABASE_URL` 環境変数の確認
   - PostgreSQL接続設定の確認

3. **重複送信**
   - キャッシュファイル `/tmp/confirmation_emails_sent.txt` の確認
   - 手動削除: `rm -f /tmp/confirmation_emails_sent.txt`

### 手動テスト

```bash
# Cron Job スクリプトの単体テスト
python3 send_confirmation_emails_cron.py

# 15分後に開始するテストセミナーの作成
python3 create_test_seminar.py

# 重複防止のテスト
python3 test_duplicate_prevention.py
```

## メンテナンス

- キャッシュファイルは日次で自動クリーンアップ
- 1000件を超えるとメモリ内キャッシュも自動クリア
- ログファイルの定期的な確認推奨

## セキュリティ注意事項

- `.env` ファイルの `DATABASE_URL` は本番環境設定のまま
- メール認証情報は環境変数で管理
- Cron Job実行ログにパスワード情報が含まれないよう注意