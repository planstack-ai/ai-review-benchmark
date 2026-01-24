# frozen_string_literal: true

class FindOrCreateRaceService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Race condition creates duplicate records
    find_or_create_by without handling
  end

  private

  def buggy_implementation
    # 実装
  end
end
