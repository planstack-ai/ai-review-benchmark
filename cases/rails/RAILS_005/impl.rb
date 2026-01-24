# frozen_string_literal: true

class CodeReviewService
  include ActiveModel::Model
  include ActiveModel::Attributes

  attribute :repository_id, :integer
  attribute :pull_request_id, :integer
  attribute :reviewer_id, :integer
  attribute :automated, :boolean, default: false

  validates :repository_id, :pull_request_id, :reviewer_id, presence: true

  def initialize(attributes = {})
    super
    @errors_found = []
    @suggestions = []
  end

  def perform_review
    return false unless valid?

    ActiveRecord::Base.transaction do
      review = create_review_record
      analyze_code_changes
      generate_review_comments
      update_pull_request_status
      
      if review.persisted?
        schedule_notifications(review)
        true
      else
        false
      end
    end
  rescue StandardError => e
    Rails.logger.error "Code review failed: #{e.message}"
    false
  end

  private

  def create_review_record
    CodeReview.create!(
      repository_id: repository_id,
      pull_request_id: pull_request_id,
      reviewer_id: reviewer_id,
      status: 'in_progress',
      automated: automated,
      started_at: Time.current
    )
  end

  def analyze_code_changes
    pull_request = PullRequest.find(pull_request_id)
    changed_files = pull_request.changed_files

    changed_files.each do |file|
      analyze_file_changes(file)
    end
  end

  def analyze_file_changes(file)
    if file.ruby_file?
      check_ruby_conventions(file)
      check_security_issues(file)
    elsif file.javascript_file?
      check_javascript_patterns(file)
    end

    check_test_coverage(file) if file.test_file?
  end

  def check_ruby_conventions(file)
    violations = RubocopAnalyzer.new(file.content).analyze
    @errors_found.concat(violations)
  end

  def check_security_issues(file)
    security_issues = SecurityScanner.new(file.content).scan
    @errors_found.concat(security_issues)
  end

  def check_javascript_patterns(file)
    eslint_issues = EslintAnalyzer.new(file.content).analyze
    @errors_found.concat(eslint_issues)
  end

  def check_test_coverage(file)
    coverage = TestCoverageAnalyzer.new(file).calculate_coverage
    if coverage < 80
      @suggestions << "Consider adding more test coverage for #{file.name}"
    end
  end

  def generate_review_comments
    @errors_found.each do |error|
      ReviewComment.create!(
        pull_request_id: pull_request_id,
        reviewer_id: reviewer_id,
        file_path: error[:file_path],
        line_number: error[:line_number],
        comment: error[:message],
        severity: error[:severity]
      )
    end
  end

  def update_pull_request_status
    pull_request = PullRequest.find(pull_request_id)
    status = @errors_found.any? ? 'changes_requested' : 'approved'
    pull_request.update!(review_status: status, reviewed_at: Time.current)
  end

  def schedule_notifications(review)
    after_save { NotifyReviewCompleteJob.perform_later(review.id) }
    after_save { UpdateMetricsJob.perform_later(repository_id) }
    
    if @errors_found.any?
      after_save { NotifyDeveloperJob.perform_later(pull_request_id, @errors_found.count) }
    end
  end
end