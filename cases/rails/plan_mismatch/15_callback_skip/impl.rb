# frozen_string_literal: true

class AdminUserUpdateService
  def initialize(user, params)
    @user = user
    @params = params
  end

  def execute
    # BUG: update_columns はバリデーションもコールバックもスキップする
    # 仕様ではバリデーションは実行すべき
    @user.update_columns(@params)
  end
end
