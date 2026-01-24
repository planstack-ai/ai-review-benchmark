# プロフィール更新API

## 概要
ユーザーが自分のプロフィールを更新する。

## 要件

1. 名前とメールアドレスのみ更新可能
2. 権限（role）は更新不可
3. Strong Parameters を使用する

## 使用すべき既存実装

- `User#update` - 更新メソッド
- Strong Parameters でパラメータを制限

## 注意事項

- Mass Assignment 脆弱性を防ぐこと
