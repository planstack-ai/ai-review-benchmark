# frozen_string_literal: true

class PerformanceAnalyticsService
  def initialize(user_id, date_range)
    @user_id = user_id
    @start_date = date_range.begin
    @end_date = date_range.end
  end

  def generate_comprehensive_report
    {
      user_metrics: fetch_user_performance_metrics,
      activity_summary: fetch_activity_summary,
      comparative_rankings: fetch_user_rankings,
      trend_analysis: calculate_performance_trends
    }
  end

  private

  def fetch_user_performance_metrics
    sql = <<~SQL
      SELECT 
        u.id,
        u.username,
        COUNT(DISTINCT a.id) as total_activities,
        AVG(a.completion_time) as avg_completion_time,
        SUM(a.points_earned) as total_points,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY a.completion_time) as median_time
      FROM users u
      LEFT JOIN activities a ON u.id = a.user_id
      WHERE u.id = $1 
        AND a.created_at BETWEEN $2 AND $3
        AND a.status = 'completed'
      GROUP BY u.id, u.username
    SQL

    result = ActiveRecord::Base.connection.exec_query(
      sql, 
      'user_performance_metrics',
      [[@user_id, nil], [@start_date, nil], [@end_date, nil]]
    )
    
    result.first || {}
  end

  def fetch_activity_summary
    sql = <<~SQL
      WITH daily_stats AS (
        SELECT 
          DATE(a.created_at) as activity_date,
          COUNT(*) as daily_count,
          AVG(a.completion_time) as daily_avg_time,
          SUM(a.points_earned) as daily_points
        FROM activities a
        WHERE a.user_id = $1 
          AND a.created_at BETWEEN $2 AND $3
          AND a.status = 'completed'
        GROUP BY DATE(a.created_at)
      )
      SELECT 
        activity_date,
        daily_count,
        daily_avg_time,
        daily_points,
        SUM(daily_count) OVER (ORDER BY activity_date) as cumulative_activities
      FROM daily_stats
      ORDER BY activity_date
    SQL

    ActiveRecord::Base.connection.exec_query(
      sql,
      'activity_summary',
      [[@user_id, nil], [@start_date, nil], [@end_date, nil]]
    ).to_a
  end

  def fetch_user_rankings
    sql = <<~SQL
      WITH user_totals AS (
        SELECT 
          u.id,
          u.username,
          SUM(a.points_earned) as total_points,
          COUNT(a.id) as activity_count,
          RANK() OVER (ORDER BY SUM(a.points_earned) DESC) as points_rank,
          RANK() OVER (ORDER BY COUNT(a.id) DESC) as activity_rank
        FROM users u
        LEFT JOIN activities a ON u.id = a.user_id
        WHERE a.created_at BETWEEN $2 AND $3
          AND a.status = 'completed'
        GROUP BY u.id, u.username
      )
      SELECT 
        points_rank,
        activity_rank,
        total_points,
        activity_count,
        (SELECT COUNT(*) FROM user_totals) as total_users
      FROM user_totals
      WHERE id = $1
    SQL

    result = ActiveRecord::Base.connection.exec_query(
      sql,
      'user_rankings',
      [[@user_id, nil], [@start_date, nil], [@end_date, nil]]
    )
    
    result.first || {}
  end

  def calculate_performance_trends
    return {} unless sufficient_data_available?

    weekly_performance = fetch_weekly_performance_data
    calculate_trend_metrics(weekly_performance)
  end

  def sufficient_data_available?
    (@end_date - @start_date).to_i >= 14
  end

  def fetch_weekly_performance_data
    sql = <<~SQL
      SELECT 
        DATE_TRUNC('week', a.created_at) as week_start,
        COUNT(*) as weekly_activities,
        AVG(a.completion_time) as avg_completion_time,
        SUM(a.points_earned) as weekly_points
      FROM activities a
      WHERE a.user_id = $1 
        AND a.created_at BETWEEN $2 AND $3
        AND a.status = 'completed'
      GROUP BY DATE_TRUNC('week', a.created_at)
      ORDER BY week_start
    SQL

    ActiveRecord::Base.connection.exec_query(
      sql,
      'weekly_performance',
      [[@user_id, nil], [@start_date, nil], [@end_date, nil]]
    ).to_a
  end

  def calculate_trend_metrics(weekly_data)
    return {} if weekly_data.length < 2

    points_trend = calculate_linear_trend(weekly_data.map { |w| w['weekly_points'].to_f })
    activity_trend = calculate_linear_trend(weekly_data.map { |w| w['weekly_activities'].to_f })

    {
      points_trend_slope: points_trend,
      activity_trend_slope: activity_trend,
      trend_direction: determine_trend_direction(points_trend, activity_trend)
    }
  end

  def calculate_linear_trend(values)
    n = values.length
    x_values = (1..n).to_a
    
    sum_x = x_values.sum
    sum_y = values.sum
    sum_xy = x_values.zip(values).map { |x, y| x * y }.sum
    sum_x_squared = x_values.map { |x| x * x }.sum
    
    (n * sum_xy - sum_x * sum_y).to_f / (n * sum_x_squared - sum_x * sum_x)
  end

  def determine_trend_direction(points_slope, activity_slope)
    if points_slope > 0 && activity_slope > 0
      'improving'
    elsif points_slope < 0 && activity_slope < 0
      'declining'
    else
      'mixed'
    end
  end
end