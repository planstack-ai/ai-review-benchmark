# frozen_string_literal: true

class EventDisplayService
  def initialize(event, user)
    @event = event
    @user = user
  end

  def formatted_start_time
    # BUG: Time.zone はアプリケーションのデフォルトタイムゾーン
    # user.timezone を使うべき
    local_time = @event.starts_at.in_time_zone(Time.zone)
    TimeFormatter.format(local_time, TimeFormatter::FORMATS[:japanese])
  end
end
