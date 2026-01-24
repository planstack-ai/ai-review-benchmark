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
#  deleted_at :datetime
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_users_on_email      (email) UNIQUE
#  index_users_on_deleted_at (deleted_at)

# == Schema Information
#
# Table name: orders
#
#  id          :bigint           not null, primary key
#  user_id     :bigint           not null
#  total_cents :integer          not null
#  status      :string           not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Indexes
#
#  index_orders_on_user_id (user_id)
#
# Foreign Keys
#
#  fk_rails_... (user_id => users.id)
```

## Models

```ruby
class User < ApplicationRecord
  has_many :orders, dependent: :destroy

  scope :active, -> { where(deleted_at: nil) }
  scope :deleted, -> { where.not(deleted_at: nil) }

  def deleted?
    deleted_at.present?
  end

  def soft_delete!
    update!(deleted_at: Time.current)
  end

  def restore!
    update!(deleted_at: nil)
  end
end

class Order < ApplicationRecord
  belongs_to :user

  STATUSES = %w[pending processing shipped delivered cancelled].freeze

  validates :status, inclusion: { in: STATUSES }
  validates :total_cents, presence: true, numericality: { greater_than: 0 }

  scope :recent, -> { order(created_at: :desc) }
  scope :by_status, ->(status) { where(status: status) }

  def total_amount
    Money.new(total_cents)
  end

  def can_be_cancelled?
    %w[pending processing].include?(status)
  end
end

class ApplicationController < ActionController::Base
  before_action :authenticate_user!
  before_action :authorize_user!

  private

  def current_user
    @current_user ||= User.find(session[:user_id]) if session[:user_id]
  end

  def authenticate_user!
    redirect_to login_path unless current_user
  end

  def authorize_user!
    redirect_to root_path if current_user&.deleted?
  end
end
```