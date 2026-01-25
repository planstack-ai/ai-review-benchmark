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
        COUNT(DISTINCT o.id) as total_orders,
        AVG(o.total_amount) as avg_order_value,
        SUM(o.total_amount) as total_revenue,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY o.total_amount) as median_order_value
      FROM users u
      LEFT JOIN orders o ON u.id = o.user_id
      WHERE u.id = $1
        AND o.created_at BETWEEN $2 AND $3
        AND o.status IN ('shipped', 'delivered')
      GROUP BY u.id
    SQL

    result = ActiveRecord::Base.connection.exec_query(
      sql,
      'user_performance_metrics',
      [@user_id, @start_date, @end_date]
    )

    result.first || {}
  end

  def fetch_activity_summary
    sql = <<~SQL
      WITH daily_stats AS (
        SELECT
          DATE(o.created_at) as order_date,
          COUNT(*) as daily_count,
          AVG(o.total_amount) as daily_avg_value,
          SUM(o.total_amount) as daily_revenue
        FROM orders o
        WHERE o.user_id = $1
          AND o.created_at BETWEEN $2 AND $3
          AND o.status IN ('shipped', 'delivered')
        GROUP BY DATE(o.created_at)
      )
      SELECT
        order_date,
        daily_count,
        daily_avg_value,
        daily_revenue,
        SUM(daily_count) OVER (ORDER BY order_date) as cumulative_orders
      FROM daily_stats
      ORDER BY order_date
    SQL

    ActiveRecord::Base.connection.exec_query(
      sql,
      'activity_summary',
      [@user_id, @start_date, @end_date]
    ).to_a
  end

  def fetch_user_rankings
    sql = <<~SQL
      WITH user_totals AS (
        SELECT
          u.id,
          SUM(o.total_amount) as total_revenue,
          COUNT(o.id) as order_count,
          RANK() OVER (ORDER BY SUM(o.total_amount) DESC) as revenue_rank,
          RANK() OVER (ORDER BY COUNT(o.id) DESC) as order_rank
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE o.created_at BETWEEN $2 AND $3
          AND o.status IN ('shipped', 'delivered')
        GROUP BY u.id
      )
      SELECT
        revenue_rank,
        order_rank,
        total_revenue,
        order_count,
        (SELECT COUNT(*) FROM user_totals) as total_users
      FROM user_totals
      WHERE id = $1
    SQL

    result = ActiveRecord::Base.connection.exec_query(
      sql,
      'user_rankings',
      [@user_id, @start_date, @end_date]
    )

    result.first || {}
  end

  def calculate_performance_trends
    return {} unless sufficient_data_available?

    weekly_performance = fetch_weekly_performance_data
    calculate_trend_metrics(weekly_performance)
  end

  def sufficient_data_available?
    return false if @start_date.nil? || @end_date.nil?
    (@end_date - @start_date).to_i >= 14
  end

  def fetch_weekly_performance_data
    sql = <<~SQL
      SELECT
        DATE_TRUNC('week', o.created_at) as week_start,
        COUNT(*) as weekly_orders,
        AVG(o.total_amount) as avg_order_value,
        SUM(o.total_amount) as weekly_revenue
      FROM orders o
      WHERE o.user_id = $1
        AND o.created_at BETWEEN $2 AND $3
        AND o.status IN ('shipped', 'delivered')
      GROUP BY DATE_TRUNC('week', o.created_at)
      ORDER BY week_start
    SQL

    ActiveRecord::Base.connection.exec_query(
      sql,
      'weekly_performance',
      [@user_id, @start_date, @end_date]
    ).to_a
  end

  def calculate_trend_metrics(weekly_data)
    return {} if weekly_data.length < 2

    revenue_trend = calculate_linear_trend(weekly_data.map { |w| w['weekly_revenue'].to_f })
    order_trend = calculate_linear_trend(weekly_data.map { |w| w['weekly_orders'].to_f })

    {
      revenue_trend_slope: revenue_trend,
      order_trend_slope: order_trend,
      trend_direction: determine_trend_direction(revenue_trend, order_trend)
    }
  end

  def calculate_linear_trend(values)
    n = values.length
    return 0.0 if n < 2
    x_values = (1..n).to_a

    sum_x = x_values.sum
    sum_y = values.sum
    sum_xy = x_values.zip(values).map { |x, y| x * y }.sum
    sum_x_squared = x_values.map { |x| x * x }.sum

    denominator = (n * sum_x_squared - sum_x * sum_x)
    return 0.0 if denominator == 0
    (n * sum_xy - sum_x * sum_y).to_f / denominator
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