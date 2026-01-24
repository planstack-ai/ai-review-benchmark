# frozen_string_literal: true

class CodeReviewBenchmarkService
  BENCHMARK_TYPES = %w[performance security maintainability].freeze
  DEFAULT_BATCH_SIZE = 100

  def initialize(repository_id, benchmark_type = 'performance')
    @repository_id = repository_id
    @benchmark_type = validate_benchmark_type(benchmark_type)
    @results = []
  end

  def execute
    return failure_result('Repository not found') unless repository_exists?

    process_code_files
    calculate_metrics
    store_benchmark_results

    success_result
  end

  def generate_report
    benchmark_data = fetch_benchmark_data
    return {} if benchmark_data.empty?

    {
      repository_id: @repository_id,
      benchmark_type: @benchmark_type,
      total_files: benchmark_data.count,
      average_score: calculate_average_score(benchmark_data),
      issues_found: count_issues(benchmark_data),
      completion_time: benchmark_data.maximum(:completed_at)
    }
  end

  private

  def validate_benchmark_type(type)
    return type if BENCHMARK_TYPES.include?(type)
    
    BENCHMARK_TYPES.first
  end

  def repository_exists?
    Repository.exists?(@repository_id)
  end

  def process_code_files
    code_files = fetch_code_files
    
    code_files.find_each(batch_size: DEFAULT_BATCH_SIZE) do |file|
      result = analyze_file(file)
      @results << result if result.present?
    end
  end

  def fetch_code_files
    Repository.find(@repository_id)
              .code_files
              .where(active: true)
              .where('file_size < ?', 1.megabyte)
  end

  def analyze_file(file)
    analyzer = create_analyzer(file)
    score = analyzer.calculate_score
    issues = analyzer.detect_issues

    {
      file_id: file.id,
      file_path: file.path,
      score: score,
      issues: issues,
      analyzed_at: Time.current
    }
  end

  def create_analyzer(file)
    case @benchmark_type
    when 'performance'
      PerformanceAnalyzer.new(file)
    when 'security'
      SecurityAnalyzer.new(file)
    else
      MaintainabilityAnalyzer.new(file)
    end
  end

  def calculate_metrics
    return if @results.empty?

    @total_score = @results.sum { |r| r[:score] }
    @average_score = @total_score.to_f / @results.size
    @issue_count = @results.sum { |r| r[:issues].size }
  end

  def store_benchmark_results
    benchmark_record = create_benchmark_record
    
    @results.each do |result|
      BenchmarkResult.create!(
        benchmark_id: benchmark_record.id,
        file_id: result[:file_id],
        score: result[:score],
        issues_data: result[:issues],
        completed_at: result[:analyzed_at]
      )
    end
  end

  def create_benchmark_record
    Benchmark.create!(
      repository_id: @repository_id,
      benchmark_type: @benchmark_type,
      total_files: @results.size,
      average_score: @average_score,
      total_issues: @issue_count,
      status: 'completed'
    )
  end

  def fetch_benchmark_data
    BenchmarkResult.joins(:benchmark)
                   .where(benchmarks: { repository_id: @repository_id, benchmark_type: @benchmark_type })
                   .where('benchmarks.created_at > ?', 30.days.ago)
  end

  def calculate_average_score(data)
    return 0 if data.empty?
    
    data.average(:score).round(2)
  end

  def count_issues(data)
    data.sum { |record| record.issues_data&.size || 0 }
  end

  def success_result
    { success: true, message: 'Benchmark completed successfully' }
  end

  def failure_result(message)
    { success: false, message: message }
  end
end