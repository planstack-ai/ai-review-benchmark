# frozen_string_literal: true

class CartManipulationService
  include ActiveModel::Model
  include ActiveModel::Attributes

  attribute :user, :object
  attribute :cart_id, :integer
  attribute :item_id, :integer
  attribute :quantity, :integer, default: 1
  attribute :action_type, :string

  validates :user, :cart_id, :item_id, :action_type, presence: true
  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :action_type, inclusion: { in: %w[add remove update clear] }

  def call
    return failure_result('Invalid parameters') unless valid?
    return failure_result('Item not found') unless item_exists?

    case action_type
    when 'add'
      add_item_to_cart
    when 'remove'
      remove_item_from_cart
    when 'update'
      update_item_quantity
    when 'clear'
      clear_cart_items
    else
      failure_result('Unknown action type')
    end
  rescue StandardError => e
    failure_result("Operation failed: #{e.message}")
  end

  private

  def add_item_to_cart
    cart = Cart.find(cart_id)
    existing_item = cart.cart_items.find_by(item_id: item_id)

    if existing_item
      existing_item.update!(quantity: existing_item.quantity + quantity)
    else
      cart.cart_items.create!(item_id: item_id, quantity: quantity)
    end

    success_result(cart.reload)
  end

  def remove_item_from_cart
    cart = Cart.find(cart_id)
    cart_item = cart.cart_items.find_by(item_id: item_id)

    return failure_result('Item not in cart') unless cart_item

    cart_item.destroy!
    success_result(cart.reload)
  end

  def update_item_quantity
    cart = Cart.find(cart_id)
    cart_item = cart.cart_items.find_by(item_id: item_id)

    return failure_result('Item not in cart') unless cart_item

    cart_item.update!(quantity: quantity)
    success_result(cart.reload)
  end

  def clear_cart_items
    cart = Cart.find(cart_id)
    cart.cart_items.destroy_all
    success_result(cart.reload)
  end

  def item_exists?
    Item.exists?(item_id)
  end

  def success_result(cart)
    {
      success: true,
      cart: cart,
      total_items: cart.cart_items.sum(:quantity),
      total_amount: calculate_total_amount(cart)
    }
  end

  def failure_result(message)
    {
      success: false,
      error: message,
      cart: nil
    }
  end

  def calculate_total_amount(cart)
    cart.cart_items.joins(:item).sum('items.price * cart_items.quantity')
  end
end