# frozen_string_literal: true

class BulkUserImportService
  BATCH_SIZE = 1000
  REQUIRED_FIELDS = %w[email first_name last_name].freeze

  def initialize(csv_file_path)
    @csv_file_path = csv_file_path
    @imported_count = 0
    @failed_records = []
  end

  def call
    validate_file_exists!
    
    CSV.foreach(@csv_file_path, headers: true, header_converters: :symbol) do |row|
      process_batch_when_ready(row)
    end
    
    insert_remaining_batch if batch_ready?
    
    {
      imported_count: @imported_count,
      failed_records: @failed_records,
      success: @failed_records.empty?
    }
  rescue StandardError => e
    Rails.logger.error "Bulk import failed: #{e.message}"
    { success: false, error: e.message }
  end

  private

  def validate_file_exists!
    raise ArgumentError, "File not found: #{@csv_file_path}" unless File.exist?(@csv_file_path)
  end

  def process_batch_when_ready(row)
    user_data = extract_user_data(row)
    
    if valid_user_data?(user_data)
      current_batch << prepare_user_attributes(user_data)
      insert_batch_if_full
    else
      @failed_records << { row: row.to_h, errors: validation_errors(user_data) }
    end
  end

  def extract_user_data(row)
    {
      email: row[:email]&.strip&.downcase,
      first_name: row[:first_name]&.strip,
      last_name: row[:last_name]&.strip,
      phone: row[:phone]&.strip,
      department: row[:department]&.strip
    }
  end

  def valid_user_data?(user_data)
    REQUIRED_FIELDS.all? { |field| user_data[field.to_sym].present? } &&
      valid_email_format?(user_data[:email])
  end

  def valid_email_format?(email)
    email.present? && email.match?(/\A[\w+\-.]+@[a-z\d\-]+(\.[a-z\d\-]+)*\.[a-z]+\z/i)
  end

  def validation_errors(user_data)
    errors = []
    REQUIRED_FIELDS.each do |field|
      errors << "#{field} is required" if user_data[field.to_sym].blank?
    end
    errors << "Invalid email format" unless valid_email_format?(user_data[:email])
    errors
  end

  def prepare_user_attributes(user_data)
    timestamp = Time.current
    user_data.merge(
      created_at: timestamp,
      updated_at: timestamp,
      status: 'active'
    )
  end

  def current_batch
    @current_batch ||= []
  end

  def insert_batch_if_full
    return unless current_batch.size >= BATCH_SIZE
    insert_current_batch
  end

  def batch_ready?
    current_batch.any?
  end

  def insert_remaining_batch
    insert_current_batch
  end

  def insert_current_batch
    User.insert_all(current_batch, unique_by: :email)
    @imported_count += current_batch.size
    @current_batch = []
  end
end