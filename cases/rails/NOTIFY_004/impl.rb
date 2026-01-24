# frozen_string_literal: true

class TemplateVariableNilService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Template variable user.name is nil causing error
    user.name
  end

  private

  def buggy_implementation
    # 実装
  end
end
