# メール送信サービス

## 概要
条件に応じてユーザーにメールを送信する。

## 要件

1. ユーザーがメール通知を有効にしている場合のみ送信する
2. ユーザーのメールアドレスが検証済みの場合のみ送信する
3. 上記条件を満たさない場合は送信せずに false を返す
4. 送信成功時は true を返す

## 使用すべき既存実装

- `User#email_notifications_enabled?` - 通知設定
- `User#email_verified?` - メールアドレス検証状態
- `NotificationMailer.send_notification(user, message)` - メール送信

## 注意事項

- 条件を満たさない場合は早期リターンすること
- 不必要なメール送信を防ぐこと
