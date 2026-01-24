# 既存コードベース情報

## セッション管理

ログイン前のパスを保存する際は `request.path` を使用（クエリ文字列なし、相対パス）

```ruby
# ログイン前
session[:return_to] = request.path  # "/products/123" など

# ログイン後
redirect_to session.delete(:return_to) || root_path
```

## 補足

- `request.path` は相対パスのみを返すため、外部URLは保存されない
- `request.fullpath` はクエリ文字列を含む
- `request.url` は完全なURLを返す（外部URL攻撃の可能性あり）
