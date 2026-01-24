# frozen_string_literal: true

class UserListService
  def fetch_users
    # BUG: includes(:orders) は全注文を読み込む（最新1件ではない）
    # また、with_latest_order スコープを使うべき
    User.active
        .includes(:orders, :profile)
        .map do |user|
          {
            id: user.id,
            name: user.display_name,
            latest_order_amount: user.orders.first&.total_amount
          }
        end
  end
end
