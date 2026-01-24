# frozen_string_literal: true

class CodeReviewBenchmarkService
  include ActiveModel::Validations

  attr_reader :repository, :pull_request, :analysis_results

  validates :repository, presence: true
  validates :pull_request, presence: true

  def initialize(repository:, pull_request:)
    @repository = repository
    @pull_request = pull_request
    @analysis_results = []
  end

  def execute
    return false unless valid?

    ActiveRecord::Base.transaction do
      benchmark_record = create_benchmark_record
      
      process_code_changes(benchmark_record)
      generate_final_report(benchmark_record)
      
      benchmark_record.update!(status: 'completed', completed_at: Time.current)
      benchmark_record
    end
  rescue StandardError => e
    Rails.logger.error "Benchmark failed: #{e.message}"
    false
  end

  private

  def create_benchmark_record
    CodeReviewBenchmark.create!(
      repository: repository,
      pull_request_id: pull_request.id,
      status: 'processing',
      started_at: Time.current
    )
  end

  def process_code_changes(benchmark_record)
    pull_request.changed_files.find_each do |file|
      ActiveRecord::Base.transaction do
        analysis_result = analyze_file_changes(file)
        store_analysis_result(benchmark_record, file, analysis_result)
        
        if analysis_result[:critical_issues].any?
          update_benchmark_priority(benchmark_record, 'high')
        end
      end
    end
  end

  def analyze_file_changes(file)
    {
      file_path: file.path,
      lines_added: file.additions,
      lines_removed: file.deletions,
      complexity_score: calculate_complexity(file),
      critical_issues: detect_critical_issues(file),
      suggestions: generate_suggestions(file)
    }
  end

  def store_analysis_result(benchmark_record, file, analysis_result)
    BenchmarkAnalysis.create!(
      benchmark: benchmark_record,
      file_path: analysis_result[:file_path],
      complexity_score: analysis_result[:complexity_score],
      issues_count: analysis_result[:critical_issues].size,
      suggestions_count: analysis_result[:suggestions].size,
      metadata: analysis_result.to_json
    )
    
    @analysis_results << analysis_result
  end

  def update_benchmark_priority(benchmark_record, priority)
    benchmark_record.update!(priority: priority)
  end

  def calculate_complexity(file)
    base_complexity = file.additions + file.deletions
    cyclomatic_multiplier = detect_control_structures(file).size * 2
    base_complexity + cyclomatic_multiplier
  end

  def detect_critical_issues(file)
    issues = []
    issues << 'security_vulnerability' if contains_security_patterns?(file)
    issues << 'performance_concern' if contains_performance_issues?(file)
    issues << 'code_smell' if contains_code_smells?(file)
    issues
  end

  def generate_suggestions(file)
    suggestions = []
    suggestions << 'Consider extracting method' if file.additions > 50
    suggestions << 'Add error handling' if missing_error_handling?(file)
    suggestions << 'Improve test coverage' if needs_more_tests?(file)
    suggestions
  end

  def generate_final_report(benchmark_record)
    total_complexity = @analysis_results.sum { |result| result[:complexity_score] }
    total_issues = @analysis_results.sum { |result| result[:critical_issues].size }
    
    benchmark_record.update!(
      total_complexity: total_complexity,
      total_issues: total_issues,
      overall_score: calculate_overall_score(total_complexity, total_issues)
    )
  end

  def calculate_overall_score(complexity, issues)
    base_score = 100
    complexity_penalty = [complexity * 0.5, 50].min
    issues_penalty = [issues * 10, 40].min
    [base_score - complexity_penalty - issues_penalty, 0].max
  end

  def detect_control_structures(file)
    %w[if unless while for case].select { |keyword| file.content.include?(keyword) }
  end

  def contains_security_patterns?(file)
    file.content.match?(/eval|system|exec|`/)
  end

  def contains_performance_issues?(file)
    file.content.match?(/N\+1|find_each|includes/)
  end

  def contains_code_smells?(file)
    file.additions > 100 || file.content.lines.any? { |line| line.length > 120 }
  end

  def missing_error_handling?(file)
    !file.content.match?(/rescue|raise|begin/)
  end

  def needs_more_tests?(file)
    file.path.match?(/app\//) && !file.path.match?(/spec\/|test\//)
  end
end