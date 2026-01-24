# frozen_string_literal: true

class UserListService
  def active_users
    # アクティブで最近ログインしたユーザーを取得
    User.where(deleted_at: nil)  # BUG: suspended条件が漏れている。User.activeスコープを使うべき
        .where('last_login_at >= ?', 30.days.ago)
        .order(created_at: :desc)
  end
end
