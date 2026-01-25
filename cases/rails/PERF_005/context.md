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
#  status     :integer          default("active"), not null
#  role       :integer          default("user"), not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_users_on_email                    (email) UNIQUE
#  index_users_on_status                   (status)
#  index_users_on_role                     (role)
#  index_users_on_status_and_role          (status, role)
#  index_users_on_created_at               (created_at)
#

# Table name: orders
#
#  id          :bigint           not null, primary key
#  user_id     :bigint           not null
#  total_cents :integer          not null
#  status      :integer          default("pending"), not null
#  order_date  :date             not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Indexes
#
#  index_orders_on_user_id                 (user_id)
#  index_orders_on_status                  (status)
#  index_orders_on_order_date              (order_date)
#  index_orders_on_user_id_and_status      (user_id, status)
#  index_orders_on_status_and_order_date   (status, order_date)
#

# Table name: products
#
#  id          :bigint           not null, primary key
#  name        :string           not null
#  category_id :bigint           not null
#  price_cents :integer          not null
#  active      :boolean          default(true), not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Indexes
#
#  index_products_on_category_id           (category_id)
#  index_products_on_active                (active)
#  index_products_on_category_id_and_active (category_id, active)
#
```

## Models

```ruby
class User < ApplicationRecord
  enum status: { active: 0, inactive: 1, suspended: 2 }
  enum role: { user: 0, admin: 1, moderator: 2 }

  has_many :orders, dependent: :destroy

  validates :email, presence: true, uniqueness: true
  validates :first_name, :last_name, presence: true

  scope :active_users, -> { where(status: :active) }
  scope :admins, -> { where(role: :admin) }
  scope :recent, -> { where(created_at: 1.month.ago..) }
  scope :by_status, ->(status) { where(status: status) }
  scope :by_role, ->(role) { where(role: role) }

  def full_name
    "#{first_name} #{last_name}"
  end
end

class Order < ApplicationRecord
  enum status: { pending: 0, processing: 1, shipped: 2, delivered: 3, cancelled: 4 }

  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items

  validates :total_cents, presence: true, numericality: { greater_than: 0 }
  validates :order_date, presence: true

  scope :completed, -> { where(status: [:shipped, :delivered]) }
  scope :active_orders, -> { where(status: [:pending, :processing, :shipped]) }
  scope :by_status, ->(status) { where(status: status) }
  scope :by_date_range, ->(start_date, end_date) { where(order_date: start_date..end_date) }
  scope :recent_orders, -> { where(order_date: 30.days.ago..) }

  def total_amount
    Money.new(total_cents)
  end
end

class Product < ApplicationRecord
  belongs_to :category
  has_many :order_items, dependent: :destroy

  validates :name, presence: true
  validates :price_cents, presence: true, numericality: { greater_than: 0 }

  scope :active_products, -> { where(active: true) }
  scope :by_category, ->(category_id) { where(category_id: category_id) }
  scope :available, -> { where(active: true) }

  def price
    Money.new(price_cents)
  end
end

class Category < ApplicationRecord
  has_many :products, dependent: :destroy

  validates :name, presence: true, uniqueness: true

  scope :with_active_products, -> { joins(:products).where(products: { active: true }).distinct }
end
```

## Usage Guidelines

- Ensure database indexes exist for columns used in WHERE clauses, ORDER BY, and JOIN conditions for optimal query performance.

