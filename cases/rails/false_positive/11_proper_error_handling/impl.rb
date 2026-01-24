# frozen_string_literal: true

class ExternalDataService
  MAX_RETRIES = 3

  def initialize(url)
    @url = url
  end

  def fetch
    Retryable.retry(times: MAX_RETRIES, on: [ExternalApi::TimeoutError]) do
      ExternalApi.fetch(@url)
    end
  rescue ExternalApi::TimeoutError, ExternalApi::ApiError => e
    Rails.logger.error("External API failed: #{e.message}")
    nil
  end
end
