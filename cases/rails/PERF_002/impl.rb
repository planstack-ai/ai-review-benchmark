# frozen_string_literal: true

class OrderBatchProcessingService
  BATCH_SIZE = 1000
  MAX_RETRY_ATTEMPTS = 3

  def initialize(status: nil, date_range: nil)
    @status = status
    @date_range = date_range
    @processed_count = 0
    @failed_count = 0
    @batch_errors = []
  end

  def call
    Rails.logger.info "Starting order batch processing for #{total_orders_count} orders"
    
    process_orders_in_batches
    
    {
      processed: @processed_count,
      failed: @failed_count,
      errors: @batch_errors,
      total: total_orders_count
    }
  end

  private

  def process_orders_in_batches
    orders_to_process.each_slice(BATCH_SIZE) do |batch|
      process_batch(batch)
    end
  end

  def orders_to_process
    scope = Order.all
    scope = scope.where(status: @status) if @status.present?
    scope = scope.where(created_at: @date_range) if @date_range.present?
    scope.includes(:customer, :order_items)
  end

  def process_batch(batch)
    batch.each do |order|
      retry_count = 0
      
      begin
        process_single_order(order)
        @processed_count += 1
      rescue StandardError => e
        retry_count += 1
        
        if retry_count <= MAX_RETRY_ATTEMPTS
          Rails.logger.warn "Retrying order #{order.id}, attempt #{retry_count}"
          retry
        else
          handle_processing_error(order, e)
        end
      end
    end
  end

  def process_single_order(order)
    validate_order_data(order)
    update_order_metrics(order)
    send_notification_if_needed(order)
    mark_order_as_processed(order)
  end

  def validate_order_data(order)
    raise "Invalid order data" if order.order_items.empty?
    raise "Missing customer information" unless order.customer.present?
  end

  def update_order_metrics(order)
    order.update!(
      processed_at: Time.current,
      total_items: order.order_items.count,
      processing_duration: calculate_processing_duration(order)
    )
  end

  def calculate_processing_duration(order)
    return 0 unless order.created_at.present?
    
    (Time.current - order.created_at).to_i
  end

  def send_notification_if_needed(order)
    return unless order.total_amount > 1000

    OrderNotificationService.new(order).send_high_value_notification
  end

  def mark_order_as_processed(order)
    order.update!(status: 'processed')
  end

  def handle_processing_error(order, error)
    @failed_count += 1
    @batch_errors << { order_id: order.id, error: error.message }
    
    Rails.logger.error "Failed to process order #{order.id}: #{error.message}"
    
    order.update!(status: 'failed', error_message: error.message)
  end

  def total_orders_count
    @total_orders_count ||= orders_to_process.count
  end
end