# frozen_string_literal: true

class UserAnalyticsService
  def initialize(user)
    @user = user
    @current_date = Date.current
  end

  def generate_monthly_report
    return {} unless @user.present?

    {
      activity_summary: calculate_activity_summary,
      engagement_metrics: calculate_engagement_metrics,
      performance_data: calculate_performance_data,
      recommendations: generate_recommendations
    }
  end

  def calculate_streak_data
    recent_activities = @user.activities.recent.order(:created_at)
    return { current_streak: 0, longest_streak: 0 } if recent_activities.empty?

    current_streak = calculate_current_streak(recent_activities)
    longest_streak = calculate_longest_streak(recent_activities)

    { current_streak: current_streak, longest_streak: longest_streak }
  end

  def export_user_data(format = :json)
    data = compile_user_data
    
    case format.to_sym
    when :csv
      generate_csv_export(data)
    when :pdf
      generate_pdf_export(data)
    else
      data.to_json
    end
  end

  private

  def calculate_activity_summary
    activities = @user.activities.where(created_at: monthly_range)
    
    {
      total_activities: activities.count,
      completed_tasks: activities.completed.count,
      average_daily_activities: calculate_daily_average(activities),
      most_active_day: find_most_active_day(activities)
    }
  end

  def calculate_engagement_metrics
    posts = @user.posts.where(created_at: monthly_range)
    comments = @user.comments.where(created_at: monthly_range)
    
    {
      posts_created: posts.count,
      comments_made: comments.count,
      likes_received: posts.sum(:likes_count),
      engagement_score: calculate_engagement_score(posts, comments)
    }
  end

  def calculate_performance_data
    completed_tasks = @user.tasks.completed.where(completed_at: monthly_range)
    
    {
      completion_rate: calculate_completion_rate,
      average_completion_time: completed_tasks.average(:completion_time_minutes),
      productivity_trend: calculate_productivity_trend(completed_tasks)
    }
  end

  def generate_recommendations
    activity_level = determine_activity_level
    engagement_level = determine_engagement_level
    
    recommendations = []
    recommendations << "Increase daily activity" if activity_level == :low
    recommendations << "Engage more with community" if engagement_level == :low
    recommendations << "Maintain current momentum" if activity_level == :high
    
    recommendations
  end

  def monthly_range
    @current_date.beginning_of_month..@current_date.end_of_month
  end

  def calculate_daily_average(activities)
    return 0 if activities.empty?
    
    days_in_month = @current_date.end_of_month.day
    activities.count.to_f / days_in_month
  end

  def find_most_active_day(activities)
    activities.group_by { |a| a.created_at.strftime('%A') }
              .max_by { |_, acts| acts.count }
              &.first || 'No activity'
  end

  def calculate_engagement_score(posts, comments)
    (posts.count * 2) + comments.count
  end

  def calculate_completion_rate
    total_tasks = @user.tasks.where(created_at: monthly_range).count
    return 0 if total_tasks.zero?
    
    completed_tasks = @user.tasks.completed.where(completed_at: monthly_range).count
    (completed_tasks.to_f / total_tasks * 100).round(2)
  end

  def determine_activity_level
    total_activities = @user.activities.where(created_at: monthly_range).count
    
    case total_activities
    when 0..10 then :low
    when 11..30 then :medium
    else :high
    end
  end

  def determine_engagement_level
    engagement_score = calculate_engagement_score(@user.posts, @user.comments)
    
    case engagement_score
    when 0..5 then :low
    when 6..20 then :medium
    else :high
    end
  end