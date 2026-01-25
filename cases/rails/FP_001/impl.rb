# frozen_string_literal: true

class UserManagementService
  attr_reader :user, :errors

  def initialize(user = nil)
    @user = user
    @errors = []
  end

  def create(user_params)
    @user = User.new(sanitized_params(user_params))
    
    if validate_user_data && @user.save
      send_welcome_email
      log_user_creation
      @user
    else
      collect_errors
      false
    end
  end

  def update(user_params)
    return false unless @user

    @user.assign_attributes(sanitized_params(user_params))
    
    if validate_user_data && @user.save
      log_user_update
      @user
    else
      collect_errors
      false
    end
  end

  def destroy
    return false unless @user

    if @user.destroy
      cleanup_user_data
      log_user_deletion
      true
    else
      collect_errors
      false
    end
  end

  def find_by_email(email)
    @user = User.find_by(email: normalize_email(email))
  end

  def activate
    return false unless @user

    attributes = { active: true }
    attributes[:activated_at] = Time.current if @user.has_attribute?(:activated_at)
    @user.update(attributes)
  end

  def deactivate
    return false unless @user

    attributes = { active: false }
    attributes[:deactivated_at] = Time.current if @user.has_attribute?(:deactivated_at)
    @user.update(attributes)
  end

  private

  def sanitized_params(params)
    return {} unless params

    allowed = [:name, :email, :role]
    allowed << :phone if User.attribute_names.include?("phone")
    params.permit(*allowed)
  end

  def validate_user_data
    if @user.email.blank?
      @user.errors.add(:email, "can't be blank")
      return false
    end

    unless valid_email_format?
      @user.errors.add(:email, "is invalid")
      return false
    end

    if duplicate_email_exists?
      @user.errors.add(:email, "has already been taken")
      return false
    end
    
    true
  end

  def valid_email_format?
    @user.email.match?(/\A[\w+\-.]+@[a-z\d\-]+(\.[a-z\d\-]+)*\.[a-z]+\z/i)
  end

  def duplicate_email_exists?
    existing_user = User.find_by(email: @user.email)
    existing_user && existing_user.id != @user.id
  end

  def normalize_email(email)
    email.to_s.downcase.strip
  end

  def collect_errors
    @errors = @user.errors.full_messages
  end

  def send_welcome_email
    UserMailer.welcome_email(@user).deliver_later
  end

  def cleanup_user_data
    @user.posts.destroy_all
    @user.comments.destroy_all if @user.respond_to?(:comments)
  end

  def log_user_creation
    Rails.logger.info "User created: #{@user.email} (ID: #{@user.id})"
  end

  def log_user_update
    Rails.logger.info "User updated: #{@user.email} (ID: #{@user.id})"
  end

  def log_user_deletion
    Rails.logger.info "User deleted: #{@user.email}"
  end
end
