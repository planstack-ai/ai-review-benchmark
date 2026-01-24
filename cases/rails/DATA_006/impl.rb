# frozen_string_literal: true

class OrderPriorityService
  PRIORITY_LEVELS = {
    low: 1,
    normal: 2,
    high: 3,
    urgent: 4
  }.freeze

  def initialize(order)
    @order = order
  end

  def update_priority(level)
    return false unless valid_priority_level?(level)

    @order.update(priority: PRIORITY_LEVELS[level.to_sym])
  end

  def calculate_processing_order(orders)
    orders.sort_by { |order| priority_weight(order) }
  end

  def escalate_overdue_orders
    overdue_orders = find_overdue_orders
    
    overdue_orders.each do |order|
      current_priority = order.priority
      new_priority = [current_priority + 1, PRIORITY_LEVELS[:urgent]].min
      order.update(priority: new_priority)
    end

    overdue_orders.count
  end

  def bulk_assign_priorities(order_ids, priority_level)
    return 0 unless valid_priority_level?(priority_level)

    priority_value = PRIORITY_LEVELS[priority_level.to_sym]
    
    Order.where(id: order_ids).update_all(priority: priority_value)
  end

  def priority_distribution
    Order.group(:priority).count.transform_keys do |priority|
      PRIORITY_LEVELS.key(priority) || :unknown
    end
  end

  private

  def valid_priority_level?(level)
    PRIORITY_LEVELS.key?(level.to_sym)
  end

  def priority_weight(order)
    base_weight = order.priority * 100
    age_factor = (Time.current - order.created_at) / 1.hour
    
    base_weight + age_factor
  end

  def find_overdue_orders
    Order.joins(:customer)
         .where('orders.created_at < ?', 2.days.ago)
         .where('orders.status != ?', 'completed')
  end

  def normalize_priority_value(value)
    return PRIORITY_LEVELS[:normal] if value.nil?
    
    [value, PRIORITY_LEVELS[:urgent]].min
  end
end