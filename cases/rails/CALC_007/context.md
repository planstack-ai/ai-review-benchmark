# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id              :bigint           not null, primary key
#  user_id         :bigint           not null
#  total_amount    :decimal(10,2)    not null
#  discount_amount :decimal(10,2)    default(0.0)
#  status          :string           not null
#  created_at      :datetime         not null
#  updated_at      :datetime         not null
#
# Table name: payments
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  amount     :decimal(10,2)    not null
#  status     :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: user_points
#
#  id         :bigint           not null, primary key
#  user_id    :bigint           not null
#  points     :integer          default(0)
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: point_transactions
#
#  id          :bigint           not null, primary key
#  user_id     :bigint           not null
#  order_id    :bigint
#  points      :integer          not null
#  reason      :string           not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :payments, dependent: :destroy
  has_many :point_transactions, dependent: :destroy

  validates :total_amount, presence: true, numericality: { greater_than: 0 }
  validates :discount_amount, numericality: { greater_than_or_equal_to: 0 }
  validates :status, presence: true

  scope :completed, -> { where(status: 'completed') }
  scope :paid, -> { joins(:payments).where(payments: { status: 'completed' }) }

  def final_amount
    total_amount - discount_amount
  end

  def paid_amount
    payments.completed.sum(:amount)
  end

  def fully_paid?
    paid_amount >= final_amount
  end
end

class Payment < ApplicationRecord
  belongs_to :order

  validates :amount, presence: true, numericality: { greater_than: 0 }
  validates :status, presence: true

  scope :completed, -> { where(status: 'completed') }
  scope :pending, -> { where(status: 'pending') }

  after_update :process_payment_completion, if: :saved_change_to_status?

  private

  def process_payment_completion
    return unless status == 'completed'
    
    PointsService.award_for_payment(self)
  end
end

class UserPoint < ApplicationRecord
  belongs_to :user

  validates :points, numericality: { greater_than_or_equal_to: 0 }

  def self.find_or_create_for_user(user)
    find_or_create_by(user: user) { |up| up.points = 0 }
  end
end

class PointTransaction < ApplicationRecord
  belongs_to :user
  belongs_to :order, optional: true

  validates :points, presence: true, numericality: { other_than: 0 }
  validates :reason, presence: true

  scope :earnings, -> { where('points > 0') }
  scope :redemptions, -> { where('points < 0') }

  REASONS = {
    purchase: 'purchase',
    bonus: 'bonus',
    redemption: 'redemption',
    refund: 'refund'
  }.freeze
end

class PointsService
  POINTS_PER_DOLLAR = 10

  def self.award_for_payment(payment)
    new(payment).award_points
  end

  def initialize(payment)
    @payment = payment
    @order = payment.order
    @user = @order.user
  end

  private

  attr_reader :payment, :order, :user
end
```