# frozen_string_literal: true

class JobOutsideAfterCommitService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Job enqueued in transaction - runs even if rollback
    after_save { NotifyJob.perform_later(id) }
  end

  private

  def buggy_implementation
    # 実装
  end
end
