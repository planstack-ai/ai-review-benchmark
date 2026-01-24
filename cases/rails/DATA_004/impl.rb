# frozen_string_literal: true

class CodeReviewBenchmarkService
  attr_reader :repository, :language, :complexity_threshold

  def initialize(repository:, language: nil, complexity_threshold: 5)
    @repository = repository
    @language = language
    @complexity_threshold = complexity_threshold
  end

  def generate_benchmark_data
    {
      total_files: count_reviewable_files,
      complexity_distribution: calculate_complexity_distribution,
      recent_reviews: fetch_recent_reviews,
      top_reviewers: identify_top_reviewers,
      language_breakdown: analyze_language_breakdown
    }
  end

  def find_files_for_review(limit: 50)
    base_query = CodeFile.joins(:repository)
                        .where(repository: repository)
                        .where('complexity_score >= ?', complexity_threshold)

    base_query = base_query.where(language: language) if language.present?
    
    base_query.order(updated_at: :desc)
              .limit(limit)
              .includes(:code_reviews, :author)
  end

  def search_reviewed_files(search_term, options = {})
    page = options[:page] || 1
    per_page = options[:per_page] || 20

    query = CodeFile.joins(:code_reviews)
                   .where(repository: repository)
                   .where('file_path ILIKE ? OR content ILIKE ?', 
                          "%#{search_term}%", "%#{search_term}%")

    query = query.where(language: language) if language.present?
    
    query.distinct
         .order(created_at: :desc)
         .page(page)
         .per(per_page)
  end

  private

  def count_reviewable_files
    find_files_for_review(limit: nil).count
  end

  def calculate_complexity_distribution
    files = find_files_for_review(limit: nil)
    
    {
      low: files.where('complexity_score < 3').count,
      medium: files.where('complexity_score BETWEEN 3 AND 7').count,
      high: files.where('complexity_score > 7').count
    }
  end

  def fetch_recent_reviews
    CodeReview.joins(:code_file)
             .where(code_files: { repository: repository })
             .where('code_reviews.created_at >= ?', 30.days.ago)
             .includes(:reviewer, :code_file)
             .order(created_at: :desc)
             .limit(10)
  end

  def identify_top_reviewers
    User.joins(code_reviews: :code_file)
        .where(code_files: { repository: repository })
        .where('code_reviews.created_at >= ?', 90.days.ago)
        .group('users.id')
        .order('COUNT(code_reviews.id) DESC')
        .limit(5)
        .pluck('users.name, COUNT(code_reviews.id)')
  end

  def analyze_language_breakdown
    CodeFile.where(repository: repository)
            .group(:language)
            .count
            .sort_by { |_, count| -count }
            .to_h
  end
end