# frozen_string_literal: true

class ArticleListService
  def fetch_articles
    # BUG: N+1 クエリが発生
    # 記事ごとに author を取得するクエリが発行される
    Article.published.map do |article|
      {
        id: article.id,
        title: article.title,
        author_name: article.author.name  # N+1 here
      }
    end
  end
end
