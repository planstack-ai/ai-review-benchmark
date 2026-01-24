# 既存コードベース情報

## ExternalApiClient

```ruby
module ExternalApiClient
  class ExternalApiError < StandardError; end

  def self.fetch(endpoint)
    response = HTTParty.get(endpoint)
    raise ExternalApiError, "API error: #{response.code}" unless response.success?
    response.body
  end
end
```

## DataParser

```ruby
module DataParser
  class ParseError < StandardError; end

  def self.parse(json_string)
    data = JSON.parse(json_string)
    raise ParseError, "Invalid format" unless data.is_a?(Hash) && data["items"]
    data["items"]
  end
end
```

## DataRecord モデル

```ruby
class DataRecord < ApplicationRecord
  validates :external_id, presence: true, uniqueness: true
  validates :payload, presence: true
end
```
