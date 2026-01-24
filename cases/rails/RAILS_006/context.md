# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: users
#
#  id         :bigint           not null, primary key
#  email      :string           not null
#  first_name :string
#  last_name  :string
#  role       :string           default("user")
#  active     :boolean          default(true)
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: posts
#
#  id          :bigint           not null, primary key
#  title       :string           not null
#  content     :text
#  status      :string           default("draft")
#  user_id     :bigint           not null
#  category_id :bigint
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Table name: categories
#
#  id          :bigint           not null, primary key
#  name        :string           not null
#  description :text
#  active      :boolean          default(true)
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  ROLES = %w[user admin moderator].freeze
  
  has_many :posts, dependent: :destroy
  
  validates :email, presence: true, uniqueness: true
  validates :role, inclusion: { in: ROLES }
  
  scope :active, -> { where(active: true) }
  scope :by_role, ->(role) { where(role: role) }
  
  def full_name
    "#{first_name} #{last_name}".strip
  end
  
  def admin?
    role == 'admin'
  end
end

class Post < ApplicationRecord
  STATUSES = %w[draft published archived].freeze
  
  belongs_to :user
  belongs_to :category, optional: true
  
  validates :title, presence: true
  validates :status, inclusion: { in: STATUSES }
  
  scope :published, -> { where(status: 'published') }
  scope :by_status, ->(status) { where(status: status) }
  scope :recent, -> { order(created_at: :desc) }
  
  def published?
    status == 'published'
  end
end

class Category < ApplicationRecord
  has_many :posts, dependent: :nullify
  
  validates :name, presence: true, uniqueness: true
  
  scope :active, -> { where(active: true) }
  scope :alphabetical, -> { order(:name) }
end
```

## Application Controller

```ruby
class ApplicationController < ActionController::Base
  protect_from_forgery with: :exception
  
  before_action :authenticate_user!
  before_action :configure_permitted_parameters, if: :devise_controller?
  
  private
  
  def configure_permitted_parameters
    devise_parameter_sanitizer.permit(:sign_up, keys: [:first_name, :last_name])
    devise_parameter_sanitizer.permit(:account_update, keys: [:first_name, :last_name])
  end
  
  def require_admin
    redirect_to root_path unless current_user&.admin?
  end
end
```