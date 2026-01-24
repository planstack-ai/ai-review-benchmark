# frozen_string_literal: true

class ActivityReportService
  def initialize(user, start_date = nil, end_date = nil)
    @user = user
    @start_date = start_date || 1.week.ago
    @end_date = end_date || Time.current
  end

  def generate_report
    {
      user_id: @user.id,
      period: report_period,
      activities: formatted_activities,
      summary: activity_summary,
      generated_at: Time.current
    }
  end

  def export_to_csv
    CSV.generate(headers: true) do |csv|
      csv << csv_headers
      
      activities_in_period.each do |activity|
        csv << format_activity_row(activity)
      end
    end
  end

  private

  def report_period
    {
      start: @start_date.strftime('%Y-%m-%d'),
      end: @end_date.strftime('%Y-%m-%d')
    }
  end

  def formatted_activities
    activities_in_period.map do |activity|
      {
        id: activity.id,
        type: activity.activity_type,
        description: activity.description,
        created_at: activity.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        duration: activity.duration_minutes,
        status: activity.status
      }
    end
  end

  def activities_in_period
    @activities_in_period ||= @user.activities
      .where(created_at: @start_date..@end_date)
      .order(:created_at)
  end

  def activity_summary
    activities = activities_in_period
    
    {
      total_count: activities.count,
      total_duration: activities.sum(:duration_minutes),
      by_type: group_by_type(activities),
      daily_breakdown: daily_activity_breakdown(activities)
    }
  end

  def group_by_type(activities)
    activities.group(:activity_type).count
  end

  def daily_activity_breakdown(activities)
    activities.group_by { |a| a.created_at.to_date }.transform_values(&:count)
  end

  def csv_headers
    ['ID', 'Type', 'Description', 'Created At', 'Duration (min)', 'Status']
  end

  def format_activity_row(activity)
    [
      activity.id,
      activity.activity_type,
      activity.description,
      activity.created_at.strftime('%Y-%m-%d %H:%M:%S'),
      activity.duration_minutes,
      activity.status
    ]
  end
end