# frozen_string_literal: true

class AsyncBenchmarkWriteService
  include ActiveModel::Validations

  BATCH_SIZE = 1000
  MAX_CONCURRENT_WRITES = 10

  validates :data_source, presence: true
  validates :output_format, inclusion: { in: %w[json csv xml] }

  def initialize(data_source:, output_format: 'json', batch_size: BATCH_SIZE)
    @data_source = data_source
    @output_format = output_format
    @batch_size = batch_size
    @write_queue = Queue.new
    @results = Concurrent::Array.new
    @error_count = Concurrent::AtomicFixnum.new(0)
  end

  def execute
    return failure_result('Invalid parameters') unless valid?

    start_time = Time.current
    setup_async_writers
    process_data_batches
    wait_for_completion
    
    {
      success: true,
      duration: Time.current - start_time,
      records_processed: @results.size,
      errors: @error_count.value,
      throughput: calculate_throughput(start_time)
    }
  rescue StandardError => e
    Rails.logger.error "AsyncBenchmarkWriteService failed: #{e.message}"
    failure_result(e.message)
  end

  private

  def setup_async_writers
    @writer_threads = MAX_CONCURRENT_WRITES.times.map do |index|
      Thread.new { async_writer_loop(index) }
    end
  end

  def process_data_batches
    @data_source.find_in_batches(batch_size: @batch_size) do |batch|
      formatted_batch = format_batch_data(batch)
      @write_queue << formatted_batch
    end
    
    MAX_CONCURRENT_WRITES.times { @write_queue << :shutdown }
  end

  def async_writer_loop(worker_id)
    loop do
      batch = @write_queue.pop
      break if batch == :shutdown
      
      write_batch_async(batch, worker_id)
    end
  rescue StandardError => e
    @error_count.increment
    Rails.logger.error "Writer #{worker_id} error: #{e.message}"
  end

  def write_batch_async(batch, worker_id)
    output_path = generate_output_path(worker_id, batch.first&.dig('id'))
    
    File.open(output_path, 'w') do |file|
      case @output_format
      when 'json'
        file.write(batch.to_json)
      when 'csv'
        write_csv_batch(file, batch)
      when 'xml'
        write_xml_batch(file, batch)
      end
    end
    
    @results.concat(batch)
  end

  def format_batch_data(batch)
    batch.map do |record|
      {
        'id' => record.id,
        'timestamp' => Time.current.iso8601,
        'data' => record.attributes.except('created_at', 'updated_at'),
        'checksum' => generate_checksum(record)
      }
    end
  end

  def write_csv_batch(file, batch)
    return if batch.empty?
    
    headers = batch.first.keys
    file.puts headers.join(',')
    
    batch.each do |row|
      file.puts headers.map { |h| row[h] }.join(',')
    end
  end

  def write_xml_batch(file, batch)
    file.puts '<?xml version="1.0" encoding="UTF-8"?>'
    file.puts '<records>'
    
    batch.each do |record|
      file.puts "  <record id=\"#{record['id']}\">"
      record.except('id').each { |k, v| file.puts "    <#{k}>#{v}</#{k}>" }
      file.puts '  </record>'
    end
    
    file.puts '</records>'
  end

  def generate_output_path(worker_id, record_id)
    timestamp = Time.current.strftime('%Y%m%d_%H%M%S')
    "tmp/benchmark_#{timestamp}_#{worker_id}_#{record_id}.#{@output_format}"
  end

  def generate_checksum(record)
    Digest::MD5.hexdigest(record.attributes.to_json)
  end

  def wait_for_completion
    @writer_threads.each(&:join)
  end

  def calculate_throughput(start_time)
    duration = Time.current - start_time
    return 0 if duration.zero?
    
    (@results.size / duration).round(2)
  end

  def failure_result(message)
    { success: false, error: message, records_processed: 0 }
  end
end