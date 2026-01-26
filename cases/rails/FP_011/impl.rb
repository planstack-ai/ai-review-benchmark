# frozen_string_literal: true

class AdminBypassService
  class UnauthorizedBypassError < StandardError; end
  class BypassDisabledError < StandardError; end

  attr_reader :admin_user, :errors

  def initialize(admin_user)
    @admin_user = admin_user
    @errors = []
  end

  def create_user(user_params, options = {})
    validate_bypass_permissions!

    skip_validation = options[:skip_validation] && admin_user.bypass_enabled?

    user = User.new(sanitized_user_params(user_params))

    if skip_validation
      log_bypass_usage(:create_user, user_params)
      user.save(validate: false)
    else
      user.save
    end

    if user.persisted?
      user
    else
      @errors = user.errors.full_messages
      nil
    end
  end

  def create_test_account(user:, account_type:, test_data: nil, expires_in: 30.days)
    validate_bypass_permissions!

    test_account = TestAccount.new(
      user: user,
      account_type: account_type,
      test_data: test_data || default_test_data(account_type),
      expires_at: expires_in.from_now
    )

    if test_account.save
      log_bypass_usage(:create_test_account, { user_id: user.id, account_type: account_type })
      test_account
    else
      @errors = test_account.errors.full_messages
      nil
    end
  end

  def bulk_create_users(users_params, options = {})
    validate_bypass_permissions!

    created_users = []
    failed_users = []

    ActiveRecord::Base.transaction do
      users_params.each do |params|
        user = create_user(params, options)
        if user
          created_users << user
        else
          failed_users << { params: params, errors: @errors.dup }
        end
      end

      raise ActiveRecord::Rollback if failed_users.any? && !options[:allow_partial]
    end

    { created: created_users, failed: failed_users }
  end

  def enable_bypass
    return false unless admin_user.admin?

    admin_user.update(admin_bypass_enabled: true)
  end

  def disable_bypass
    admin_user.update(admin_bypass_enabled: false)
  end

  private

  def validate_bypass_permissions!
    raise UnauthorizedBypassError, "Only admins can use bypass features" unless admin_user&.admin?
  end

  def sanitized_user_params(params)
    params.permit(:email, :first_name, :last_name, :role, :status)
  end

  def default_test_data(account_type)
    case account_type
    when 'demo'
      { features: %w[basic], limitations: { max_projects: 3 } }
    when 'sandbox'
      { features: %w[basic advanced], limitations: { max_projects: 10 } }
    when 'staging'
      { features: %w[basic advanced premium], limitations: {} }
    else
      {}
    end
  end

  def log_bypass_usage(action, details)
    Rails.logger.info(
      "[ADMIN_BYPASS] User: #{admin_user.email} (ID: #{admin_user.id}), " \
      "Action: #{action}, Details: #{details.to_json}, Time: #{Time.current}"
    )
  end
end
