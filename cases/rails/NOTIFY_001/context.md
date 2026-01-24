# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id                    :bigint           not null, primary key
#  user_id              :bigint           not null
#  status               :string           not null
#  total_amount         :decimal(10,2)    not null
#  confirmation_sent_at :datetime
#  created_at           :datetime         not null
#  updated_at           :datetime         not null
#
# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  price      :decimal(8,2)     not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: users
#
#  id         :bigint           not null, primary key
#  email      :string           not null
#  name       :string           not null
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
  
  validates :status, presence: true, inclusion: { in: %w[pending confirmed shipped delivered cancelled] }
  validates :total_amount, presence: true, numericality: { greater_than: 0 }
  
  scope :confirmed, -> { where(status: 'confirmed') }
  scope :pending_confirmation, -> { where(status: 'confirmed', confirmation_sent_at: nil) }
  scope :confirmation_sent, -> { where.not(confirmation_sent_at: nil) }
  
  def confirmed?
    status == 'confirmed'
  end
  
  def confirmation_email_sent?
    confirmation_sent_at.present?
  end
  
  def mark_confirmation_sent!
    update!(confirmation_sent_at: Time.current)
  end
  
  def customer_email
    user.email
  end
  
  def order_number
    "ORD-#{id.to_s.rjust(6, '0')}"
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product
  
  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price, presence: true, numericality: { greater_than: 0 }
end

class Product < ApplicationRecord
  has_many :order_items, dependent: :destroy
  has_many :orders, through: :order_items
  
  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
end
```

```ruby
class OrderMailer < ApplicationMailer
  default from: 'orders@example.com'
  
  def confirmation_email(order)
    @order = order
    @user = order.user
    @order_items = order.order_items.includes(:product)
    
    mail(
      to: @order.customer_email,
      subject: "Order Confirmation - #{@order.order_number}"
    )
  end
end
```

```ruby
class OrdersController < ApplicationController
  before_action :authenticate_user!
  before_action :set_order, only: [:show, :confirm]
  
  def show
  end
  
  def confirm
    if @order.update(status: 'confirmed')
      redirect_to @order, notice: 'Order confirmed successfully.'
    else
      render :show, alert: 'Unable to confirm order.'
    end
  end
  
  private
  
  def set_order
    @order = current_user.orders.find(params[:id])
  end
end
```