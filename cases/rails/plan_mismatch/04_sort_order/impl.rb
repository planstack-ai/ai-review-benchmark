# frozen_string_literal: true

class ArticlesController < ApplicationController
  def index
    @articles = Article.published
                       .order(published_at: :asc)  # BUG: :desc であるべき（新しい順）
                       .limit(20)

    render json: @articles
  end
end
