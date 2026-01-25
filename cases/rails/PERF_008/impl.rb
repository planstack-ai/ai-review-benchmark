# frozen_string_literal: true

class UserMetricsService
  def initialize(user)
    @user = user
    @metrics = {}
  end

  def update_denormalized_metrics
    calculate_activity_metrics
    calculate_engagement_metrics
    calculate_performance_metrics
    persist_metrics
  end

  def refresh_user_summary
    summary_data = build_summary_data
    @user.update!(
      total_posts: summary_data[:posts_count],
      total_likes: summary_data[:likes_received],
      total_comments: summary_data[:comments_count],
      engagement_score: summary_data[:engagement_score],
      last_activity_at: summary_data[:last_activity],
      metrics_updated_at: Time.current
    )
  end

  def bulk_update_metrics(user_ids)
    User.where(id: user_ids).find_each do |user|
      service = self.class.new(user)
      service.update_denormalized_metrics
    end
  end

  private

  def calculate_activity_metrics
    @metrics[:posts_count] = @user.posts.published.count
    @metrics[:comments_count] = @user.comments.visible.count
    @metrics[:last_activity] = [@user.posts.maximum(:created_at), @user.comments.maximum(:created_at)].compact.max
  end

  def calculate_engagement_metrics
    @metrics[:likes_received] = Like.joins(:post).where(posts: { user_id: @user.id }).count
    @metrics[:shares_received] = Share.joins(:post).where(posts: { user_id: @user.id }).count
    @metrics[:engagement_score] = calculate_engagement_score
  end

  def calculate_performance_metrics
    recent_posts = @user.posts.where('created_at > ?', 30.days.ago)
    @metrics[:avg_likes_per_post] = recent_posts.joins(:likes).group('posts.id').average('likes.count').to_f.round(2)
    @metrics[:trending_score] = calculate_trending_score(recent_posts)
  end

  def calculate_engagement_score
    base_score = @metrics[:likes_received] * 1.0 + @metrics[:shares_received] * 2.0
    activity_multiplier = [@metrics[:posts_count] / 10.0, 1.0].min + 1.0
    (base_score * activity_multiplier).round(2)
  end

  def calculate_trending_score(posts)
    return 0.0 if posts.empty?
    
    recent_engagement = posts.joins(:likes, :shares)
                            .where('likes.created_at > ? OR shares.created_at > ?', 7.days.ago, 7.days.ago)
                            .count
    
    (recent_engagement / posts.count.to_f * 100).round(2)
  end

  def build_summary_data
    {
      posts_count: @metrics[:posts_count],
      likes_received: @metrics[:likes_received],
      comments_count: @metrics[:comments_count],
      engagement_score: @metrics[:engagement_score],
      last_activity: @metrics[:last_activity]
    }
  end

  def persist_metrics
    UserMetric.upsert({
      user_id: @user.id,
      posts_count: @metrics[:posts_count],
      comments_count: @metrics[:comments_count],
      likes_received: @metrics[:likes_received],
      shares_received: @metrics[:shares_received],
      engagement_score: @metrics[:engagement_score],
      avg_likes_per_post: @metrics[:avg_likes_per_post],
      trending_score: @metrics[:trending_score],
      last_activity_at: @metrics[:last_activity],
      updated_at: Time.current
    }, unique_by: :user_id)
  end
end