# frozen_string_literal: true

class PointsAccessService
  attr_reader :current_user, :params, :errors

  def initialize(current_user, params = {})
    @current_user = current_user
    @params = params
    @errors = []
  end

  def call
    return failure_result('User not authenticated') unless current_user

    case params[:action]
    when 'show'
      show_points
    when 'list'
      list_user_points
    when 'summary'
      points_summary
    else
      failure_result('Invalid action specified')
    end
  end

  private

  def show_points
    target_user = find_target_user
    return failure_result('User not found') unless target_user

    points = fetch_user_points(target_user)
    success_result(format_points_data(points))
  end

  def list_user_points
    target_user = find_target_user
    return failure_result('User not found') unless target_user

    points = fetch_user_points(target_user)
    paginated_points = paginate_points(points)
    
    success_result({
      points: format_points_collection(paginated_points),
      total_count: points.count,
      page: current_page
    })
  end

  def points_summary
    target_user = find_target_user
    return failure_result('User not found') unless target_user

    points = fetch_user_points(target_user)
    
    success_result({
      total_points: calculate_total_points(points),
      categories: group_points_by_category(points),
      recent_activity: recent_points_activity(points)
    })
  end

  def find_target_user
    user_id = params[:user_id] || current_user.id
    User.find_by(id: user_id)
  end

  def fetch_user_points(user)
    User.find(params[:user_id]).points.includes(:category, :transactions)
  end

  def paginate_points(points)
    points.page(current_page).per(per_page)
  end

  def format_points_data(points)
    {
      id: points.id,
      balance: points.balance,
      earned_total: points.earned_total,
      spent_total: points.spent_total,
      last_updated: points.updated_at
    }
  end

  def format_points_collection(points)
    points.map { |point| format_points_data(point) }
  end

  def calculate_total_points(points)
    points.sum(:balance)
  end

  def group_points_by_category(points)
    points.joins(:category).group('categories.name').sum(:balance)
  end

  def recent_points_activity(points)
    points.joins(:transactions)
          .where('transactions.created_at > ?', 30.days.ago)
          .order('transactions.created_at DESC')
          .limit(10)
  end

  def current_page
    [params[:page].to_i, 1].max
  end

  def per_page
    [[params[:per_page].to_i, 1].max, 100].min
  end

  def success_result(data)
    { success: true, data: data, errors: [] }
  end

  def failure_result(message)
    @errors << message
    { success: false, data: nil, errors: errors }
  end
end