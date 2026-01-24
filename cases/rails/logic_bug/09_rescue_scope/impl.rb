# frozen_string_literal: true

class ExternalDataSyncService
  API_ENDPOINT = "https://api.example.com/data"

  def execute
    response = fetch_data
    return nil unless response

    items = parse_data(response)
    return nil unless items

    save_records(items)
  rescue StandardError => e
    # BUG: This rescue is too late - it won't catch errors from fetch_data or parse_data
    # because they have their own begin/rescue blocks that return nil
    Rails.logger.error("Sync failed: #{e.message}")
    nil
  end

  private

  def fetch_data
    ExternalApiClient.fetch(API_ENDPOINT)
  rescue ExternalApiClient::ExternalApiError => e
    Rails.logger.error("API error: #{e.message}")
    nil
  end

  def parse_data(response)
    DataParser.parse(response)
  # BUG: Wrong exception class - should be DataParser::ParseError
  # JSON::ParserError is raised by JSON.parse, but DataParser wraps it
  rescue JSON::ParserError => e
    Rails.logger.error("Parse error: #{e.message}")
    nil
  end

  def save_records(items)
    items.map do |item|
      DataRecord.create!(external_id: item["id"], payload: item)
    end
  end
end
