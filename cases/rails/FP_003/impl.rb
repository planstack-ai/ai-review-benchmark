# frozen_string_literal: true

class CodeReviewBenchmarkService
  attr_reader :project, :pull_request, :errors

  def initialize(project, pull_request)
    @project = project
    @pull_request = pull_request
    @errors = []
  end

  def execute
    return false unless valid_inputs?

    benchmark = create_benchmark
    return false unless benchmark.persisted?

    process_code_files(benchmark)
    generate_review_metrics(benchmark)
    finalize_benchmark(benchmark)

    benchmark
  end

  private

  def valid_inputs?
    validate_project && validate_pull_request
  end

  def validate_project
    if project.nil? || !project.persisted?
      @errors << "Invalid project provided"
      return false
    end
    true
  end

  def validate_pull_request
    if pull_request.nil? || pull_request.files.empty?
      @errors << "Pull request must contain files"
      return false
    end
    true
  end

  def create_benchmark
    project.code_review_benchmarks.create(
      pull_request: pull_request,
      status: 'processing',
      started_at: Time.current
    )
  end

  def process_code_files(benchmark)
    pull_request.files.includes(:code_metrics).each do |file|
      next unless reviewable_file?(file)

      review_result = analyze_file(file)
      benchmark.review_results.create(
        file: file,
        score: review_result[:score],
        issues_found: review_result[:issues],
        complexity_rating: review_result[:complexity]
      )
    end
  end

  def reviewable_file?(file)
    return false if file.deleted?
    return false unless file.extension.in?(%w[.rb .js .py .java])
    
    file.lines_changed > 0
  end

  def analyze_file(file)
    base_score = calculate_base_score(file)
    issues = detect_issues(file)
    complexity = assess_complexity(file)

    {
      score: [base_score - (issues.count * 5), 0].max,
      issues: issues,
      complexity: complexity
    }
  end

  def calculate_base_score(file)
    return 100 if file.code_metrics.blank?
    
    metrics = file.code_metrics.first
    score = 100
    score -= (metrics.cyclomatic_complexity - 10) * 2 if metrics.cyclomatic_complexity > 10
    score -= (metrics.method_length - 20) if metrics.method_length > 20
    
    [score, 0].max
  end

  def detect_issues(file)
    issues = []
    issues << 'Long method detected' if file.has_long_methods?
    issues << 'High complexity' if file.code_metrics&.first&.cyclomatic_complexity.to_i > 15
    issues << 'Missing tests' unless file.has_corresponding_test?
    issues
  end

  def assess_complexity(file)
    return 'low' if file.lines_changed < 10
    return 'high' if file.lines_changed > 100
    
    'medium'
  end

  def generate_review_metrics(benchmark)
    results = benchmark.review_results.includes(:file)
    
    benchmark.update(
      total_files: results.count,
      average_score: results.average(:score).to_f.round(2),
      total_issues: results.sum { |r| r.issues_found.count },
      completion_percentage: calculate_completion_percentage(results)
    )
  end

  def calculate_completion_percentage(results)
    return 0 if results.empty?
    
    completed_files = results.count { |r| r.score > 70 }
    (completed_files.to_f / results.count * 100).round(2)
  end

  def finalize_benchmark(benchmark)
    benchmark.update(
      status: 'completed',
      completed_at: Time.current
    )
    
    notify_completion(benchmark) if benchmark.project.notifications_enabled?
  end

  def notify_completion(benchmark)
    CodeReviewNotificationJob.perform_later(benchmark.id)
  end
end