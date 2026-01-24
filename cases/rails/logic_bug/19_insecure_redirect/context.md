# 既存コードベース情報

## リダイレクトの安全な実装

```ruby
module RedirectHelper
  def safe_redirect_path(url)
    uri = URI.parse(url)
    # パスのみを返す（ホストは無視）
    uri.path.presence || "/"
  rescue URI::InvalidURIError
    "/"
  end

  def internal_url?(url)
    uri = URI.parse(url)
    uri.host.nil? || uri.host == request.host
  rescue URI::InvalidURIError
    false
  end
end
```

## セッション

```ruby
# ログイン前のURLを保存
session[:return_to] = request.fullpath

# ログイン後にリダイレクト
redirect_to session.delete(:return_to) || root_path
```
