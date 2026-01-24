# frozen_string_literal: true

class TransferService
  def initialize(sender:, receiver:, amount:)
    @sender = sender
    @receiver = receiver
    @amount = amount
  end

  def execute
    # BUG: トランザクションがない
    # withdraw の後に deposit が失敗すると残高が消失する
    @sender.withdraw(@amount)
    @receiver.deposit(@amount)
    Transfer.create!(sender: @sender, receiver: @receiver, amount: @amount)
  end
end
