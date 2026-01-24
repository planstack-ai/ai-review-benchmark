# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: users
#
#  id         :bigint           not null, primary key
#  email      :string           not null
#  role       :string           default("user"), not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: products
#
#  id          :bigint           not null, primary key
#  name        :string           not null
#  price_cents :integer          not null
#  description :text
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
```

## Models

```ruby
class User < ApplicationRecord
  ROLES = %w[user admin].freeze
  
  validates :email, presence: true, uniqueness: true
  validates :role, inclusion: { in: ROLES }
  
  scope :admins, -> { where(role: 'admin') }
  scope :regular_users, -> { where(role: 'user') }
  
  def admin?
    role == 'admin'
  end
  
  def regular_user?
    role == 'user'
  end
end

class Product < ApplicationRecord
  validates :name, presence: true
  validates :price_cents, presence: true, numericality: { greater_than: 0 }
  
  scope :by_name, -> { order(:name) }
  scope :expensive, -> { where('price_cents > ?', 10000) }
  
  def price
    Money.new(price_cents, 'USD')
  end
  
  def price=(amount)
    if amount.is_a?(Money)
      self.price_cents = amount.cents
    else
      self.price_cents = (amount.to_f * 100).to_i
    end
  end
  
  def formatted_price
    price.format
  end
end

class ApplicationController < ActionController::Base
  before_action :authenticate_user!
  
  protected
  
  def current_user
    @current_user ||= User.find(session[:user_id]) if session[:user_id]
  end
  
  def authenticate_user!
    redirect_to login_path unless current_user
  end
  
  def require_admin
    redirect_to root_path, alert: 'Access denied.' unless current_user&.admin?
  end
end
```