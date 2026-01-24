# frozen_string_literal: true

class SoftDeleteInQueryService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Deleted records appear in search results
    no deleted_at filter
  end

  private

  def buggy_implementation
    # 実装
  end
end
