# frozen_string_literal: true

class UniqueConstraintMissingService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Unique constraint missing - duplicate emails allowed
    validates :email, uniqueness: true (without DB constraint)
  end

  private

  def buggy_implementation
    # 実装
  end
end
