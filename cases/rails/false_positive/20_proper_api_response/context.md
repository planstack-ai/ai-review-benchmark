# 既存コードベース情報

## ApiResponse

```ruby
module ApiResponse
  def self.success(data, status: :ok)
    { json: { data: data }, status: status }
  end

  def self.error(message, status: :bad_request)
    { json: { error: { message: message } }, status: status }
  end

  def self.created(data)
    success(data, status: :created)
  end

  def self.not_found(message = "Resource not found")
    error(message, status: :not_found)
  end
end
```
