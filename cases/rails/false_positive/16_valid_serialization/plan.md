# ユーザーJSON出力サービス

## 概要
ユーザー情報をJSON形式で出力する。

## 要件

1. 公開情報のみを出力する（id, name, created_at）
2. 機密情報は出力しない（email, password_digest, role）
3. 関連データは含めない

## 使用すべき既存実装

- `User#as_json` または明示的なハッシュ構築

## 注意事項

- 機密情報の漏洩を防ぐこと
