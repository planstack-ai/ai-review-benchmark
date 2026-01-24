# Existing Codebase

## Schema

```ruby
# db/schema.rb
# create_table "orders", force: :cascade do |t|
#   t.string "status", null: false
#   t.decimal "total_amount", precision: 10, scale: 2
#   t.bigint "user_id", null: false
#   t.datetime "created_at", null: false
#   t.datetime "updated_at", null: false
#   t.index ["user_id"], name: "index_orders_on_user_id"
#   t.index ["status"], name: "index_orders_on_status"
# end

# create_table "users", force: :cascade do |t|
#   t.string "email", null: false
#   t.string "first_name"
#   t.string "last_name"
#   t.datetime "created_at", null: false
#   t.datetime "updated_at", null: false
# end
```

## Models

```ruby
# app/models/user.rb
class User < ApplicationRecord
  has_many :orders, dependent: :destroy
  
  validates :email, presence: true, uniqueness: true
  
  def full_name
    "#{first_name} #{last_name}".strip
  end
end

# app/models/order.rb
class Order < ApplicationRecord
  belongs_to :user
  
  validates :status, presence: true
  validates :total_amount, presence: true, numericality: { greater_than: 0 }
  
  scope :recent, -> { order(created_at: :desc) }
  scope :by_status, ->(status) { where(status: status) }
  
  def pending?
    status == 'pending'
  end
  
  def processing?
    status == 'processing'
  end
  
  def shipped?
    status == 'shipped'
  end
  
  def delivered?
    status == 'delivered'
  end
  
  def cancelled?
    status == 'cancelled'
  end
  
  def can_be_cancelled?
    pending? || processing?
  end
  
  def fulfillable?
    pending?
  end
  
  private
  
  def valid_status_transition?(new_status)
    case status
    when 'pending'
      %w[processing cancelled].include?(new_status)
    when 'processing'
      %w[shipped cancelled].include?(new_status)
    when 'shipped'
      %w[delivered].include?(new_status)
    else
      false
    end
  end
end

# app/controllers/orders_controller.rb
class OrdersController < ApplicationController
  before_action :set_order, only: [:show, :update]
  
  def index
    @orders = current_user.orders.recent
    @orders = @orders.by_status(params[:status]) if params[:status].present?
  end
  
  def show
  end
  
  def update
    if @order.update(order_params)
      redirect_to @order, notice: 'Order updated successfully.'
    else
      render :show, alert: 'Failed to update order.'
    end
  end
  
  private
  
  def set_order
    @order = current_user.orders.find(params[:id])
  end
  
  def order_params
    params.require(:order).permit(:status)
  end
end
```