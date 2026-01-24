# frozen_string_literal: true

class DateFormatService
  def initialize(user)
    @user = user
  end

  def format(date)
    return "" if date.nil?

    Time.use_zone(@user.timezone) do
      I18n.l(date.in_time_zone.to_date, locale: :ja)
    end
  end
end
