# frozen_string_literal: true

class RefundProcessingService
  include ActiveModel::Validations

  attr_reader :payment, :refund_amount, :reason, :errors

  validates :payment, presence: true
  validates :refund_amount, presence: true, numericality: { greater_than: 0 }
  validates :reason, presence: true

  def initialize(payment:, refund_amount:, reason:)
    @payment = payment
    @refund_amount = refund_amount.to_f
    @reason = reason
    @errors = []
  end

  def call
    return failure_result unless valid?
    return failure_result unless payment_refundable?

    ActiveRecord::Base.transaction do
      process_refund
      create_refund_record
      notify_customer
      log_refund_activity
    end

    success_result
  rescue StandardError => e
    @errors << "Refund processing failed: #{e.message}"
    failure_result
  end

  private

  def payment_refundable?
    unless payment.paid?
      @errors << "Payment must be in paid status to process refund"
      return false
    end

    if refund_amount > payment.amount
      @errors << "Refund amount cannot exceed payment amount"
      return false
    end

    if payment.refunds.sum(:amount) + refund_amount > payment.amount
      @errors << "Total refunds cannot exceed payment amount"
      return false
    end

    true
  end

  def process_refund
    gateway_response = payment_gateway.refund(
      transaction_id: payment.transaction_id,
      amount: refund_amount
    )

    unless gateway_response.success?
      raise "Gateway refund failed: #{gateway_response.error_message}"
    end

    @gateway_refund_id = gateway_response.refund_id
  end

  def create_refund_record
    payment.refunds.create!(
      amount: refund_amount,
      reason: reason,
      gateway_refund_id: @gateway_refund_id,
      processed_at: Time.current,
      processed_by: current_user&.id
    )
  end

  def notify_customer
    RefundNotificationMailer.refund_processed(
      payment: payment,
      refund_amount: refund_amount,
      reason: reason
    ).deliver_later
  end

  def log_refund_activity
    ActivityLogger.log(
      action: 'refund_processed',
      resource: payment,
      details: {
        refund_amount: refund_amount,
        reason: reason,
        gateway_refund_id: @gateway_refund_id
      }
    )
  end

  def payment_gateway
    @payment_gateway ||= PaymentGateway.new(payment.gateway_type)
  end

  def current_user
    Current.user
  end

  def success_result
    OpenStruct.new(success?: true, errors: [])
  end

  def failure_result
    OpenStruct.new(success?: false, errors: errors)
  end
end