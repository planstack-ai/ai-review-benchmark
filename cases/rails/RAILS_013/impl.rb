# frozen_string_literal: true

# Account transfer service
# Handles fund transfers between accounts
class TransferService
  def initialize(from_account_id:, to_account_id:, amount:)
    @from_account_id = from_account_id
    @to_account_id = to_account_id
    @amount = amount
  end

  def call
    validate_amount!

    ActiveRecord::Base.transaction do
      from_account = Account.find(from_account_id)
      to_account = Account.find(to_account_id)

      raise InsufficientFunds if from_account.balance < amount

      from_account.update!(balance: from_account.balance - amount)
      to_account.update!(balance: to_account.balance + amount)

      Transfer.create!(
        from_account: from_account,
        to_account: to_account,
        amount: amount
      )
    end

    true
  end

  private

  attr_reader :from_account_id, :to_account_id, :amount

  def validate_amount!
    raise ArgumentError, "Amount must be positive" if amount <= 0
  end
end
