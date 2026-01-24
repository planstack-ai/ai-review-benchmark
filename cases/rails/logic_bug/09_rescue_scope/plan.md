# 外部API連携サービス

## 概要
外部APIを呼び出してデータを取得し、保存する。

## 要件

1. 外部APIからデータを取得する
2. 取得したデータをパースしてDBに保存する
3. API呼び出しエラーの場合は nil を返し、ログを記録する
4. パースエラーの場合も nil を返し、ログを記録する

## 使用すべき既存実装

- `ExternalApiClient.fetch(endpoint)` - API呼び出し（失敗時は ExternalApiError を発生）
- `DataParser.parse(response)` - レスポンスをパース（失敗時は ParseError を発生）
- `Rails.logger.error` - エラーログ記録

## 注意事項

- 全ての例外を適切にハンドリングすること
- エラー時もアプリケーションが停止しないようにすること
