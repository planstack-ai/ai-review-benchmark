# Existing Codebase

## Schema

```ruby
# db/schema.rb

# create_table "users", force: :cascade do |t|
#   t.string "email", null: false
#   t.string "first_name"
#   t.string "last_name"
#   t.string "status", default: "active"
#   t.datetime "created_at", null: false
#   t.datetime "updated_at", null: false
#   t.index ["email"], name: "index_users_on_email", unique: true
# end

# create_table "orders", force: :cascade do |t|
#   t.bigint "user_id", null: false
#   t.decimal "total_amount", precision: 10, scale: 2
#   t.string "currency", default: "USD"
#   t.string "status", default: "pending"
#   t.datetime "created_at", null: false
#   t.datetime "updated_at", null: false
#   t.index ["user_id"], name: "index_orders_on_user_id"
#   t.index ["created_at"], name: "index_orders_on_created_at"
# end

# create_table "products", force: :cascade do |t|
#   t.string "name", null: false
#   t.text "description"
#   t.decimal "price", precision: 10, scale: 2
#   t.string "category"
#   t.boolean "featured", default: false
#   t.datetime "created_at", null: false
#   t.datetime "updated_at", null: false
#   t.index ["name"], name: "index_products_on_name"
#   t.index ["featured"], name: "index_products_on_featured"
# end
```

## Models

```ruby
# app/models/user.rb
class User < ApplicationRecord
  VALID_STATUSES = %w[active inactive suspended].freeze

  has_many :orders, dependent: :destroy

  validates :email, presence: true, uniqueness: true
  validates :status, inclusion: { in: VALID_STATUSES }

  scope :active, -> { where(status: 'active') }
  scope :inactive, -> { where(status: 'inactive') }

  def full_name
    "#{first_name} #{last_name}".strip
  end

  def active?
    status == 'active'
  end
end

# app/models/order.rb
class Order < ApplicationRecord
  VALID_STATUSES = %w[pending processing shipped delivered cancelled].freeze
  SUPPORTED_CURRENCIES = %w[USD EUR GBP].freeze

  belongs_to :user

  validates :total_amount, presence: true, numericality: { greater_than: 0 }
  validates :status, inclusion: { in: VALID_STATUSES }
  validates :currency, inclusion: { in: SUPPORTED_CURRENCIES }

  scope :pending, -> { where(status: 'pending') }
  scope :completed, -> { where(status: ['shipped', 'delivered']) }
  scope :recent, -> { where('created_at > ?', 30.days.ago) }

  def pending?
    status == 'pending'
  end

  def completed?
    %w[shipped delivered].include?(status)
  end
end

# app/models/product.rb
class Product < ApplicationRecord
  CATEGORIES = %w[electronics clothing books home sports].freeze

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
  validates :category, inclusion: { in: CATEGORIES }

  scope :featured, -> { where(featured: true) }
  scope :by_category, ->(cat) { where(category: cat) }
  scope :affordable, -> { where('price < ?', 50) }

  def featured?
    featured == true
  end

  def expensive?
    price > 100
  end
end
```