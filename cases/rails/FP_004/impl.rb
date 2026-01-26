# frozen_string_literal: true

class UserActivityService
  DEFAULT_INACTIVE_DAYS = 30
  DEFAULT_RECENT_DAYS = 7

  attr_reader :user, :inactive_threshold

  def initialize(user, inactive_threshold: DEFAULT_INACTIVE_DAYS)
    @user = user
    @inactive_threshold = inactive_threshold
  end

  def activity_summary
    return {} unless @user

    {
      status: @user.status,
      total_posts: user_posts.count,
      total_comments: user_comments.count,
      recent_activity: recent_activity_count,
      last_activity_at: last_activity_date
    }
  end

  def active?
    return false unless @user
    return false unless @user.active?

    recent_activity_count > 0
  end

  def inactive?
    return false unless @user
    return true if @user.inactive? || @user.suspended?

    last_activity = last_activity_date
    return true if last_activity.nil?

    last_activity < inactive_threshold.days.ago
  end

  def recent_posts
    return [] unless @user

    user_posts.where(created_at: DEFAULT_RECENT_DAYS.days.ago..)
              .recent
              .limit(10)
  end

  def recent_comments
    return [] unless @user

    user_comments.where(created_at: DEFAULT_RECENT_DAYS.days.ago..)
                 .recent
                 .limit(10)
  end

  def engagement_score
    return 0 unless @user

    posts_score = user_posts.published.count * 10
    comments_score = user_comments.approved.count * 2

    posts_score + comments_score
  end

  private

  def user_posts
    @user.posts
  end

  def user_comments
    @user.comments
  end

  def recent_activity_count
    return 0 unless @user

    recent_threshold = DEFAULT_RECENT_DAYS.days.ago

    posts_count = user_posts.where(created_at: recent_threshold..).count
    comments_count = user_comments.where(created_at: recent_threshold..).count

    posts_count + comments_count
  end

  def last_activity_date
    return nil unless @user

    last_post = user_posts.maximum(:created_at)
    last_comment = user_comments.maximum(:created_at)

    [last_post, last_comment].compact.max
  end
end
