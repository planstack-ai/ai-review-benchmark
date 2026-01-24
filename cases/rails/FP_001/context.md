# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: users
#
#  id         :bigint           not null, primary key
#  email      :string           not null
#  name       :string           not null
#  role       :string           default("user"), not null
#  active     :boolean          default(true), not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_users_on_email  (email) UNIQUE
#

# Table name: posts
#
#  id          :bigint           not null, primary key
#  title       :string           not null
#  content     :text
#  status      :string           default("draft"), not null
#  user_id     :bigint           not null
#  published_at :datetime
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Indexes
#
#  index_posts_on_user_id  (user_id)
#  index_posts_on_status   (status)
#
# Foreign Keys
#
#  fk_rails_...  (user_id => users.id)
```

## Models

```ruby
class User < ApplicationRecord
  ROLES = %w[user admin moderator].freeze
  
  has_many :posts, dependent: :destroy
  
  validates :email, presence: true, uniqueness: true, format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :name, presence: true, length: { minimum: 2, maximum: 100 }
  validates :role, inclusion: { in: ROLES }
  
  scope :active, -> { where(active: true) }
  scope :by_role, ->(role) { where(role: role) }
  scope :recent, -> { order(created_at: :desc) }
  
  def admin?
    role == 'admin'
  end
  
  def can_moderate?
    %w[admin moderator].include?(role)
  end
end

class Post < ApplicationRecord
  STATUSES = %w[draft published archived].freeze
  
  belongs_to :user
  
  validates :title, presence: true, length: { minimum: 5, maximum: 200 }
  validates :content, length: { maximum: 10000 }
  validates :status, inclusion: { in: STATUSES }
  validates :published_at, presence: true, if: :published?
  
  scope :published, -> { where(status: 'published') }
  scope :draft, -> { where(status: 'draft') }
  scope :by_status, ->(status) { where(status: status) }
  scope :recent, -> { order(created_at: :desc) }
  scope :by_author, ->(user) { where(user: user) }
  
  before_save :set_published_at, if: :will_save_change_to_status?
  
  def published?
    status == 'published'
  end
  
  def can_be_edited_by?(current_user)
    return false unless current_user
    user == current_user || current_user.can_moderate?
  end
  
  private
  
  def set_published_at
    if status == 'published' && published_at.blank?
      self.published_at = Time.current
    elsif status != 'published'
      self.published_at = nil
    end
  end
end

class ApplicationController < ActionController::Base
  protect_from_forgery with: :exception
  
  before_action :authenticate_user!
  before_action :configure_permitted_parameters, if: :devise_controller?
  
  protected
  
  def configure_permitted_parameters
    devise_parameter_sanitizer.permit(:sign_up, keys: [:name])
    devise_parameter_sanitizer.permit(:account_update, keys: [:name])
  end
  
  def require_admin
    redirect_to root_path unless current_user&.admin?
  end
end
```