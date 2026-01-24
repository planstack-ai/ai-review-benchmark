# 既存コードベース情報

## Order モデル

```ruby
class Order < ApplicationRecord
  has_many :order_items
  belongs_to :user

  enum status: { pending: 0, confirmed: 1, shipped: 2 }

  after_save :reduce_stock, if: :saved_change_to_status?
  after_save :send_confirmation_email, if: :just_confirmed?

  def confirm!
    update!(status: :confirmed)
  end

  private

  def just_confirmed?
    saved_change_to_status? && confirmed?
  end

  def reduce_stock
    return unless confirmed?
    order_items.each { |item| item.product.decrement!(:stock, item.quantity) }
  end

  def send_confirmation_email
    OrderMailer.confirmation(self).deliver_later
  end
end
```
