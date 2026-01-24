# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: sales
#
#  id         :bigint           not null, primary key
#  name       :string           not null
#  start_date :date             not null
#  end_date   :date             not null
#  active     :boolean          default(true), not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: products
#
#  id         :bigint           not null, primary key
#  name       :string           not null
#  price      :decimal(10,2)    not null
#  sale_id    :bigint
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: orders
#
#  id         :bigint           not null, primary key
#  total      :decimal(10,2)    not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class Sale < ApplicationRecord
  has_many :products, dependent: :nullify
  
  validates :name, presence: true
  validates :start_date, :end_date, presence: true
  validate :end_date_after_start_date
  
  scope :active, -> { where(active: true) }
  scope :by_date_range, ->(start_date, end_date) { where(start_date: start_date..end_date) }
  
  def duration_in_days
    (end_date - start_date).to_i + 1
  end
  
  def overlaps_with?(other_sale)
    start_date <= other_sale.end_date && end_date >= other_sale.start_date
  end
  
  private
  
  def end_date_after_start_date
    return unless start_date && end_date
    
    errors.add(:end_date, "must be after start date") if end_date < start_date
  end
end

class Product < ApplicationRecord
  belongs_to :sale, optional: true
  
  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
  
  scope :on_sale, -> { joins(:sale).merge(Sale.active) }
  scope :regular_price, -> { where(sale_id: nil) }
  
  def discounted?
    sale_id.present?
  end
end

class Order < ApplicationRecord
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items
  
  validates :total, presence: true, numericality: { greater_than: 0 }
  
  scope :recent, -> { where(created_at: 1.week.ago..) }
  scope :by_date, ->(date) { where(created_at: date.beginning_of_day..date.end_of_day) }
  
  def placed_during_sale?(sale)
    return false unless sale
    
    order_date = created_at.to_date
    order_date >= sale.start_date && order_date <= sale.end_date
  end
end

class ApplicationRecord < ActiveRecord::Base
  primary_abstract_class
  
  def self.current_time_zone
    Time.zone || Time
  end
end
```