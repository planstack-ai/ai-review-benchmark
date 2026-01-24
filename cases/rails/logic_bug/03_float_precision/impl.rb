# frozen_string_literal: true

class TransactionSummaryService
  THRESHOLD = 1000.0

  def initialize(transactions)
    @transactions = transactions
  end

  def total_amount
    # BUG: Converting BigDecimal to Float loses precision
    # Should keep as BigDecimal or use .sum directly
    @transactions.map { |t| t.amount.to_f }.sum
  end

  def exceeds_threshold?
    # BUG: Float comparison can be unreliable due to precision issues
    # Example: 0.1 + 0.2 == 0.3 returns false in floating point
    total_amount >= THRESHOLD
  end

  def formatted_total
    # This compounds the precision error
    format("%.2f", total_amount)
  end
end
