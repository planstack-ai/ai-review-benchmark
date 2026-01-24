# frozen_string_literal: true

class UserRegistrationService
  include ActiveModel::Validations

  attr_reader :user, :errors

  def initialize(user_params)
    @user_params = user_params
    @errors = []
  end

  def call
    return false unless valid_params?

    ActiveRecord::Base.transaction do
      create_user
      send_welcome_email if @user.persisted?
      log_registration_event
    end

    @user.persisted?
  rescue ActiveRecord::RecordInvalid => e
    @errors << e.message
    false
  rescue StandardError => e
    @errors << "Registration failed: #{e.message}"
    false
  end

  def success?
    @user&.persisted? && @errors.empty?
  end

  private

  def valid_params?
    return false if @user_params.blank?

    required_fields = [:email, :first_name, :last_name, :password]
    missing_fields = required_fields.select { |field| @user_params[field].blank? }

    if missing_fields.any?
      @errors << "Missing required fields: #{missing_fields.join(', ')}"
      return false
    end

    validate_email_format
    validate_password_strength

    @errors.empty?
  end

  def validate_email_format
    email = @user_params[:email]
    unless email.match?(/\A[\w+\-.]+@[a-z\d\-]+(\.[a-z\d\-]+)*\.[a-z]+\z/i)
      @errors << "Invalid email format"
    end
  end

  def validate_password_strength
    password = @user_params[:password]
    if password.length < 8
      @errors << "Password must be at least 8 characters long"
    end

    unless password.match?(/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
      @errors << "Password must contain at least one uppercase letter, one lowercase letter, and one number"
    end
  end

  def create_user
    @user = User.new(@user_params)
    @user.email = normalize_email(@user.email)
    @user.status = 'pending_verification'
    @user.verification_token = generate_verification_token

    @user.save!
  end

  def normalize_email(email)
    email.strip.downcase
  end

  def generate_verification_token
    SecureRandom.urlsafe_base64(32)
  end

  def send_welcome_email
    UserMailer.welcome_email(@user).deliver_later
  end

  def log_registration_event
    Rails.logger.info "User registered: #{@user.email} (ID: #{@user.id})"
  end
end