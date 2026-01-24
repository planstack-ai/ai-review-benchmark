# frozen_string_literal: true

class ActiveUserService
  def fetch
    User.active.recently_logged_in(30).by_created_at
  end
end
