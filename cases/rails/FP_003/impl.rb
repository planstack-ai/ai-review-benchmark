# frozen_string_literal: true

class UserProfileService
  attr_reader :user, :errors

  def initialize(user = nil)
    @user = user
    @errors = []
  end

  def create(params)
    @user = User.new(sanitized_params(params))

    if @user.save
      log_action(:created)
      @user
    else
      collect_errors
      nil
    end
  end

  def update(params)
    return add_error("User not found") unless @user

    if @user.update(sanitized_params(params))
      log_action(:updated)
      @user
    else
      collect_errors
      nil
    end
  end

  def find(id)
    @user = User.find_by(id: id)
    add_error("User not found") unless @user
    @user
  end

  def find_by_email(email)
    @user = User.find_by(email: normalize_email(email))
    add_error("User not found") unless @user
    @user
  end

  def destroy
    return add_error("User not found") unless @user

    if @user.destroy
      log_action(:deleted)
      true
    else
      collect_errors
      false
    end
  end

  def projects
    return [] unless @user

    Project.where(user_id: @user.id).recent
  end

  def assigned_tasks
    return [] unless @user

    Task.where(assignee_id: @user.id)
  end

  def comments
    return [] unless @user

    Comment.where(author_id: @user.id).recent
  end

  private

  def sanitized_params(params)
    params.permit(:name, :email, :role)
  end

  def normalize_email(email)
    email.to_s.downcase.strip
  end

  def collect_errors
    @errors = @user.errors.full_messages
  end

  def add_error(message)
    @errors << message
    nil
  end

  def log_action(action)
    Rails.logger.info "User #{action}: #{@user.email} (ID: #{@user.id})"
  end
end
