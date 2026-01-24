# frozen_string_literal: true

class DependentDestroyMissingService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: dependent: :destroy missing - children orphaned on parent delete
    has_many :items
  end

  private

  def buggy_implementation
    # 実装
  end
end
