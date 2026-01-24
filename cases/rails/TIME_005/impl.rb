# frozen_string_literal: true

class MonthEndProcessingService
  include ActiveModel::Validations

  attr_reader :processing_date, :account_id, :errors

  def initialize(account_id:, processing_date: Date.current)
    @account_id = account_id
    @processing_date = processing_date
    @errors = []
  end

  def call
    return false unless valid_processing_date?
    return false unless account_exists?

    ActiveRecord::Base.transaction do
      calculate_month_end_balances
      generate_monthly_statements
      schedule_next_processing
      update_account_status
    end

    true
  rescue StandardError => e
    @errors << "Processing failed: #{e.message}"
    false
  end

  private

  def valid_processing_date?
    return true if processing_date.is_a?(Date)

    @errors << "Invalid processing date"
    false
  end

  def account_exists?
    return true if Account.exists?(account_id)

    @errors << "Account not found"
    false
  end

  def calculate_month_end_balances
    transactions = fetch_monthly_transactions
    
    balance_summary = {
      opening_balance: fetch_opening_balance,
      total_credits: transactions.credits.sum(:amount),
      total_debits: transactions.debits.sum(:amount),
      closing_balance: 0
    }

    balance_summary[:closing_balance] = balance_summary[:opening_balance] + 
                                      balance_summary[:total_credits] - 
                                      balance_summary[:total_debits]

    store_balance_summary(balance_summary)
  end

  def generate_monthly_statements
    statement = MonthlyStatement.create!(
      account_id: account_id,
      statement_date: processing_date,
      period_start: processing_date.beginning_of_month,
      period_end: processing_date.end_of_month,
      status: 'generated'
    )

    StatementMailer.monthly_statement(statement.id).deliver_later
  end

  def schedule_next_processing
    next_month = processing_date.month + 1
    next_year = processing_date.year
    
    if next_month > 12
      next_month = 1
      next_year += 1
    end

    next_processing_date = Date.new(next_year, next_month, processing_date.day)
    
    ScheduledJob.create!(
      account_id: account_id,
      job_type: 'month_end_processing',
      scheduled_at: next_processing_date,
      parameters: { account_id: account_id }
    )
  end

  def update_account_status
    Account.find(account_id).update!(
      last_processed_at: processing_date,
      processing_status: 'completed'
    )
  end

  def fetch_monthly_transactions
    Transaction.where(
      account_id: account_id,
      created_at: processing_date.beginning_of_month..processing_date.end_of_month
    )
  end

  def fetch_opening_balance
    last_balance = AccountBalance.where(
      account_id: account_id,
      balance_date: ...processing_date.beginning_of_month
    ).order(:balance_date).last

    last_balance&.closing_balance || 0
  end

  def store_balance_summary(summary)
    AccountBalance.create!(
      account_id: account_id,
      balance_date: processing_date,
      opening_balance: summary[:opening_balance],
      closing_balance: summary[:closing_balance],
      total_credits: summary[:total_credits],
      total_debits: summary[:total_debits]
    )
  end
end