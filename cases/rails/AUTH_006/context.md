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
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: points
#
#  id          :bigint           not null, primary key
#  user_id     :bigint           not null
#  amount      :integer          not null
#  description :string
#  earned_at   :datetime         not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Table name: point_transactions
#
#  id         :bigint           not null, primary key
#  user_id    :bigint           not null
#  points_id  :bigint           not null
#  amount     :integer          not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  has_many :points, dependent: :destroy
  has_many :point_transactions, dependent: :destroy

  validates :email, presence: true, uniqueness: true
  validates :name, presence: true

  def total_points
    points.sum(:amount)
  end

  def available_points
    total_points - point_transactions.sum(:amount)
  end
end

class Point < ApplicationRecord
  belongs_to :user
  has_many :point_transactions, dependent: :destroy

  validates :amount, presence: true, numericality: { greater_than: 0 }
  validates :earned_at, presence: true

  scope :recent, -> { order(earned_at: :desc) }
  scope :for_user, ->(user) { where(user: user) }
  scope :earned_between, ->(start_date, end_date) { where(earned_at: start_date..end_date) }

  def self.total_for_user(user)
    for_user(user).sum(:amount)
  end
end

class PointTransaction < ApplicationRecord
  belongs_to :user
  belongs_to :points, class_name: 'Point'

  validates :amount, presence: true, numericality: { greater_than: 0 }

  scope :for_user, ->(user) { where(user: user) }
  scope :recent, -> { order(created_at: :desc) }

  def self.total_spent_by_user(user)
    for_user(user).sum(:amount)
  end
end

class ApplicationController < ActionController::Base
  before_action :authenticate_user!
  before_action :set_current_user

  protected

  def authenticate_user!
    redirect_to login_path unless user_signed_in?
  end

  def user_signed_in?
    current_user.present?
  end

  def current_user
    @current_user ||= User.find(session[:user_id]) if session[:user_id]
  end

  def set_current_user
    @current_user = current_user
  end

  def authorize_resource_owner!(resource)
    unless resource.user == current_user
      render json: { error: 'Unauthorized' }, status: :forbidden
    end
  end
end
```