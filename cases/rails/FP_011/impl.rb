# frozen_string_literal: true

class CodeReviewBenchmarkService
  attr_reader :repository, :pull_request, :admin_user

  def initialize(repository:, pull_request:, admin_user: nil)
    @repository = repository
    @pull_request = pull_request
    @admin_user = admin_user
  end

  def execute
    return create_benchmark_result unless should_validate?

    validation_result = validate_pull_request
    return validation_result unless validation_result.success?

    create_benchmark_result
  end

  private

  def should_validate?
    return false if admin_bypass_enabled?
    return false if testing_environment?
    
    repository.validation_enabled?
  end

  def admin_bypass_enabled?
    admin_user&.has_role?(:admin) && admin_user.bypass_validation?
  end

  def testing_environment?
    Rails.env.test? || Rails.env.development?
  end

  def validate_pull_request
    validator = PullRequestValidator.new(pull_request)
    validator.validate
  end

  def create_benchmark_result
    benchmark_data = collect_benchmark_metrics
    
    result = BenchmarkResult.create!(
      repository: repository,
      pull_request: pull_request,
      metrics: benchmark_data,
      created_by: admin_user,
      status: determine_status(benchmark_data)
    )

    notify_stakeholders(result) if result.persisted?
    
    ServiceResult.success(data: result)
  rescue StandardError => e
    ServiceResult.failure(error: e.message)
  end

  def collect_benchmark_metrics
    {
      lines_of_code: calculate_lines_of_code,
      complexity_score: calculate_complexity,
      test_coverage: calculate_test_coverage,
      performance_score: calculate_performance_score,
      security_score: calculate_security_score
    }
  end

  def calculate_lines_of_code
    pull_request.changed_files.sum(&:additions)
  end

  def calculate_complexity
    ComplexityAnalyzer.new(pull_request.diff).analyze
  end

  def calculate_test_coverage
    CoverageCalculator.new(pull_request).calculate
  end

  def calculate_performance_score
    PerformanceAnalyzer.new(pull_request).score
  end

  def calculate_security_score
    SecurityScanner.new(pull_request).scan_score
  end

  def determine_status(metrics)
    return 'excellent' if metrics.values.all? { |score| score >= 90 }
    return 'good' if metrics.values.all? { |score| score >= 70 }
    return 'needs_improvement' if metrics.values.any? { |score| score < 50 }
    
    'acceptable'
  end

  def notify_stakeholders(result)
    BenchmarkNotificationJob.perform_later(result.id)
  end
end