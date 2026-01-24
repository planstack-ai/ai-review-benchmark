# frozen_string_literal: true

class ArticleAuthorizationService
  def initialize(user:, article:)
    @user = user
    @article = article
  end

  def can_edit?
    author? || admin?
  end

  private

  def author?
    @article.author_id == @user.id
  end

  def admin?
    @user.admin?
  end
end
