# frozen_string_literal: true

class AuthorizationService
  ROLE_HIERARCHY = {
    'admin' => 100,
    'manager' => 75,
    'editor' => 50,
    'viewer' => 25,
    'guest' => 0
  }.freeze

  RESOURCE_PERMISSIONS = {
    'Project' => {
      'create' => ['admin', 'manager'],
      'read' => ['admin', 'manager', 'editor', 'viewer'],
      'update' => ['admin', 'manager', 'editor'],
      'delete' => ['admin', 'manager']
    },
    'User' => {
      'create' => ['admin'],
      'read' => ['admin', 'manager'],
      'update' => ['admin'],
      'delete' => ['admin']
    },
    'Report' => {
      'create' => ['admin', 'manager', 'editor'],
      'read' => ['admin', 'manager', 'editor', 'viewer'],
      'update' => ['admin', 'manager', 'editor'],
      'delete' => ['admin', 'manager']
    }
  }.freeze

  def initialize(user)
    @user = user
    @user_roles = extract_user_roles
  end

  def can?(action, resource_class, resource = nil)
    return false unless valid_action_and_resource?(action, resource_class)
    return false if user_suspended?

    if resource&.respond_to?(:owner_id)
      return true if owns_resource?(resource)
    end

    has_permission_for_action?(action, resource_class) || has_hierarchical_access?(resource)
  end

  def accessible_resources(resource_class, action = 'read')
    return [] unless can?(action, resource_class)

    if highest_user_role_level >= ROLE_HIERARCHY['manager']
      resource_class.constantize.all
    else
      resource_class.constantize.where(owner_id: @user.id)
    end
  end

  private

  def extract_user_roles
    return ['guest'] unless @user&.roles&.any?
    
    @user.roles.pluck(:name).uniq
  end

  def valid_action_and_resource?(action, resource_class)
    action.present? && resource_class.present? && 
    RESOURCE_PERMISSIONS.key?(resource_class.to_s)
  end

  def user_suspended?
    @user&.suspended_at&.> Time.current
  end

  def owns_resource?(resource)
    resource.owner_id == @user.id
  end

  def has_permission_for_action?(action, resource_class)
    allowed_roles = RESOURCE_PERMISSIONS.dig(resource_class.to_s, action.to_s)
    return false unless allowed_roles

    (@user_roles & allowed_roles).any?
  end

  def has_hierarchical_access?(resource)
    return false unless resource&.respond_to?(:required_role_level)
    
    highest_user_role_level >= (ROLE_HIERARCHY[resource.required_role_level] || 0)
  end

  def highest_user_role_level
    @highest_user_role_level ||= @user_roles.map { |role| ROLE_HIERARCHY[role] || 0 }.max || 0
  end
end