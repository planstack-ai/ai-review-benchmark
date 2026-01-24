# 既存コードベース情報

## ExternalApi

```ruby
module ExternalApi
  class TimeoutError < StandardError; end
  class ApiError < StandardError; end

  def self.fetch(url)
    # API呼び出し実装
  end
end
```

## Retryable

```ruby
module Retryable
  def self.retry(times:, on:)
    attempts = 0
    begin
      attempts += 1
      yield
    rescue *on => e
      retry if attempts < times
      raise
    end
  end
end
```
