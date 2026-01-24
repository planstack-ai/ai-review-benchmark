# 既存コードベース情報

## ApiToken モデル

```ruby
class ApiToken < ApplicationRecord
  belongs_to :user

  before_create :generate_token

  private

  def generate_token
    self.token = SecureRandom.hex(32)
  end
end
```

## 安全な比較

```ruby
# タイミング攻撃を防ぐ安全な文字列比較
# 比較対象の長さに関わらず一定時間で完了する
ActiveSupport::SecurityUtils.secure_compare(a, b)
```

## スキーマ

```ruby
create_table "api_tokens", force: :cascade do |t|
  t.bigint "user_id", null: false
  t.string "token", null: false
  t.datetime "expires_at"
  t.index ["token"], name: "index_api_tokens_on_token", unique: true
end
```
