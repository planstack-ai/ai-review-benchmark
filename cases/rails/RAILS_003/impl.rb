# frozen_string_literal: true

class DocumentProcessingService
  include ActiveModel::Model
  include ActiveModel::Callbacks

  define_model_callbacks :save

  attr_accessor :document, :content, :metadata, :processed_content, :validation_errors

  before_save :validate_content_format
  before_save :sanitize_content
  before_save :extract_metadata
  before_save :process_content

  def initialize(document)
    @document = document
    @content = document.raw_content
    @metadata = {}
    @processed_content = nil
    @validation_errors = []
  end

  def call
    return failure_result unless valid_document?
    
    run_callbacks :save do
      persist_document
    end

    success_result
  rescue StandardError => e
    error_result(e.message)
  end

  private

  def valid_document?
    document.present? && content.present?
  end

  def validate_content_format
    return if content.blank?

    unless content.is_a?(String)
      validation_errors << "Content must be a string"
      return
    end

    if content.length > 50_000
      validation_errors << "Content exceeds maximum length"
    end
  end

  def sanitize_content
    return if validation_errors.any?

    @content = content.strip
    @content = content.gsub(/\r\n/, "\n")
    @content = content.gsub(/[^\x00-\x7F]/, "")
  end

  def extract_metadata
    return if validation_errors.any?

    @metadata[:word_count] = content.split.length
    @metadata[:line_count] = content.lines.count
    @metadata[:character_count] = content.length
    @metadata[:processed_at] = Time.current
  end

  def process_content
    return if validation_errors.any?

    @processed_content = content.downcase
    @processed_content = processed_content.gsub(/\s+/, " ")
    @processed_content = apply_business_rules(processed_content)
  end

  def apply_business_rules(text)
    text.gsub(/\b(confidential|private|secret)\b/i, "[REDACTED]")
  end

  def persist_document
    return false if validation_errors.any?

    document.update!(
      processed_content: processed_content,
      metadata: metadata,
      status: "processed"
    )
  end

  def success_result
    {
      success: true,
      document: document,
      metadata: metadata
    }
  end

  def failure_result
    {
      success: false,
      errors: ["Invalid document provided"]
    }
  end

  def error_result(message)
    {
      success: false,
      errors: [message]
    }
  end
end