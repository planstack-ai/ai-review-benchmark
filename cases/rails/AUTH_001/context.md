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
# Table name: orders
#
#  id          :bigint           not null, primary key
#  user_id     :bigint           not null
#  total_cents :integer          not null
#  status      :string           not null
#  order_date  :datetime         not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  price_cents :integer         not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  has_many :orders, dependent: :destroy
  
  validates :email, presence: true, uniqueness: true
  validates :name, presence: true
end

class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items
  
  validates :total_cents, presence: true, numericality: { greater_than: 0 }
  validates :status, presence: true, inclusion: { in: %w[pending confirmed shipped delivered cancelled] }
  validates :order_date, presence: true
  
  scope :for_user, ->(user) { where(user: user) }
  scope :recent, -> { order(order_date: :desc) }
  scope :by_status, ->(status) { where(status: status) }
  
  def total_amount
    Money.new(total_cents)
  end
  
  def belongs_to_user?(user)
    self.user_id == user.id
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product
  
  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price_cents, presence: true, numericality: { greater_than: 0 }
  
  def line_total
    Money.new(price_cents * quantity)
  end
end

class ApplicationController < ActionController::Base
  before_action :authenticate_user!
  
  private
  
  def current_user
    @current_user ||= User.find(session[:user_id]) if session[:user_id]
  end
  
  def authenticate_user!
    redirect_to login_path unless current_user
  end
  
  def authorize_resource!(resource)
    raise ActiveRecord::RecordNotFound unless resource.user == current_user
  end
end
```