# frozen_string_literal: true

class UserRegistrationService
  include ActiveModel::Model
  include ActiveModel::Attributes

  attribute :email, :string
  attribute :password, :string
  attribute :password_confirmation, :string
  attribute :first_name, :string
  attribute :last_name, :string
  attribute :terms_accepted, :boolean, default: false

  validates :email, presence: true, format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :password, presence: true, length: { minimum: 8 }
  validates :password_confirmation, presence: true
  validates :first_name, presence: true, length: { minimum: 2, maximum: 50 }
  validates :last_name, presence: true, length: { minimum: 2, maximum: 50 }
  validates :terms_accepted, acceptance: true
  validate :passwords_match
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

  def passwords_match
    return if password.blank? || password_confirmation.blank?

    errors.add(:password_confirmation, "doesn't match password") if password != password_confirmation
  end

  def email_uniqueness
    return if email.blank?

    errors.add(:email, "has already been taken") if User.exists?(email: email)
  end

  def create_user
    User.create!(
      email: email,
      password: password,
      first_name: first_name,
      last_name: last_name,
      confirmed_at: Time.current
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