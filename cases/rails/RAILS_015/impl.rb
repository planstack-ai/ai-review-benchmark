# frozen_string_literal: true

# Order status query service
# Provides methods to query orders by status for operations dashboard
class OrderQueryService
  # Get all pending orders awaiting processing
  # Includes legacy orders that should be treated as pending
  def pending_orders
    Order.pending
  end

  # Get orders needing attention (pending or failed)
  def orders_needing_attention
    Order.where(status: [:pending, :failed])
  end

  # Get pending orders within date range
  def pending_orders_in_range(start_date, end_date)
    Order.pending.in_date_range(start_date, end_date)
  end

  # Get order counts by status for dashboard
  def status_counts
    {
      pending: Order.pending.count,
      processing: Order.processing.count,
      shipped: Order.shipped.count,
      delivered: Order.delivered.count,
      cancelled: Order.cancelled.count,
      failed: Order.failed.count
    }
  end

  # Get recent orders by status
  def recent_orders_by_status(status)
    Order.where(status: status).recent
  end
end
