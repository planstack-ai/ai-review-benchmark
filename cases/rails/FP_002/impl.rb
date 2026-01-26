# frozen_string_literal: true

class UserRegistrationService
  include ActiveModel::Model
  include ActiveModel::Attributes

  attribute :email, :string
  attribute :first_name, :string
  attribute :last_name, :string
  attribute :phone, :string

  validates :email, presence: true, format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :first_name, presence: true, length: { minimum: 2, maximum: 50 }
  validates :last_name, presence: true, length: { minimum: 2, maximum: 50 }
  validates :phone, format: { with: /\A\+?[\d\s\-\(\)]{10,15}\z/ }, allow_blank: true
  validate :email_uniqueness

  def initialize(attributes = {})
    super
    normalize_attributes
  end

  def call
    return failure_result unless valid?

    ActiveRecord::Base.transaction do
      user = create_user
      send_welcome_email(user)
      success_result(user)
    end
  rescue StandardError => e
    Rails.logger.error "User registration failed: #{e.message}"
    failure_result("Registration failed. Please try again.")
  end

  private

  def normalize_attributes
    self.email = email&.downcase&.strip
    self.first_name = first_name&.strip&.titleize
    self.last_name = last_name&.strip&.titleize
  end

  def email_uniqueness
    return if email.blank?

    errors.add(:email, "has already been taken") if User.exists?(email: email)
  end

  def create_user
    User.create!(
      email: email,
      first_name: first_name,
      last_name: last_name,
      phone: phone,
      status: :active
    )
  end

  def send_welcome_email(user)
    UserMailer.welcome_email(user).deliver_later
  end

  def success_result(user)
    OpenStruct.new(success: true, user: user, errors: [])
  end

  def failure_result(message = nil)
    error_messages = message ? [message] : errors.full_messages
    OpenStruct.new(success: false, user: nil, errors: error_messages)
  end
end
