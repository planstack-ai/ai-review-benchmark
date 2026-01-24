# APIレスポンスサービス

## 概要
統一されたAPIレスポンス形式で返す。

## 要件

1. 成功時は data キーにデータを含める
2. 失敗時は error キーにエラー情報を含める
3. HTTPステータスコードを適切に設定する

## 使用すべき既存実装

- `ApiResponse.success(data)` - 成功レスポンス
- `ApiResponse.error(message, status)` - エラーレスポンス

## 注意事項

- レスポンス形式を統一すること
