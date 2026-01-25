# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id              :bigint           not null, primary key
#  status          :string           not null
#  shipping_cost   :decimal(8,2)
#  shipping_method :string
#  shipping_error  :text
#  created_at      :datetime         not null
#  updated_at      :datetime         not null
#
# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  price      :decimal(8,2)     not null
#  weight     :decimal(8,3)
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class Order < ApplicationRecord
  STATUSES = %w[pending confirmed shipped delivered cancelled].freeze
  SHIPPING_METHODS = %w[standard express overnight].freeze

  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items

  validates :status, inclusion: { in: STATUSES }
  validates :shipping_method, inclusion: { in: SHIPPING_METHODS }, allow_nil: true

  scope :pending_shipping, -> { where(status: 'confirmed', shipping_cost: nil) }
  scope :with_shipping_errors, -> { where.not(shipping_error: nil) }

  def total_weight
    order_items.sum { |item| item.weight * item.quantity }
  end

  def shipping_address
    {
      street: "123 Main St",
      city: "Anytown",
      state: "CA",
      zip: "12345",
      country: "US"
    }
  end

  def requires_shipping_calculation?
    confirmed? && shipping_cost.nil?
  end

  def mark_as_shipped!
    update!(status: 'shipped')
  end

  private

  def confirmed?
    status == 'confirmed'
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price, presence: true, numericality: { greater_than: 0 }
  validates :weight, presence: true, numericality: { greater_than: 0 }
end

class Product < ApplicationRecord
  has_many :order_items
  has_many :orders, through: :order_items

  validates :name, presence: true
  validates :weight, presence: true, numericality: { greater_than: 0 }
end
```

```ruby
class ShippingApiError < StandardError
  attr_reader :code, :response_body

  def initialize(message, code: nil, response_body: nil)
    super(message)
    @code = code
    @response_body = response_body
  end

  def retryable?
    code.in?([500, 502, 503, 504, 'timeout'])
  end
end

class ShippingRateService
  API_TIMEOUT = 10.seconds
  MAX_RETRIES = 3

  def initialize(order)
    @order = order
  end

  def calculate_rate
    response = make_api_request
    parse_shipping_cost(response)
  rescue Net::TimeoutError => e
    raise ShippingApiError.new("Request timeout", code: 'timeout')
  rescue Net::HTTPError => e
    raise ShippingApiError.new("HTTP error: #{e.message}", code: e.response&.code)
  end

  private

  attr_reader :order

  def make_api_request
    # Simulated API call that can fail
    raise Net::TimeoutError if rand < 0.1
    raise Net::HTTPError.new("Service unavailable", double(code: 503)) if rand < 0.05
    
    { cost: 9.99, method: 'standard' }
  end

  def parse_shipping_cost(response)
    response[:cost]
  end
end
```
