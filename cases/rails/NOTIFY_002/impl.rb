# frozen_string_literal: true

class CodeReviewBenchmarkService
  include ActiveModel::Model
  
  attr_accessor :repository_url, :branch_name, :user_id
  
  def initialize(attributes = {})
    super
    @benchmark_results = []
    @analysis_complete = false
  end
  
  def execute_benchmark
    return false unless valid_repository?
    
    benchmark_job_id = enqueue_analysis_job
    update_user_status('processing')
    
    benchmark_job_id.present?
  end
  
  def process_repository_analysis
    clone_repository
    run_static_analysis
    generate_complexity_metrics
    create_benchmark_report
    finalize_results
  rescue => e
    logger.error("Benchmark analysis failed: #{e.message}")
    cleanup_temporary_files
  end
  
  private
  
  def valid_repository?
    repository_url.present? && 
    repository_url.match?(/\A(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?\z/i) &&
    user_id.present?
  end
  
  def enqueue_analysis_job
    CodeReviewBenchmarkJob.perform_async(
      repository_url: repository_url,
      branch_name: branch_name || 'main',
      user_id: user_id,
      service_instance_id: object_id
    )
  end
  
  def update_user_status(status)
    User.find(user_id).update(benchmark_status: status)
  end
  
  def clone_repository
    @temp_dir = Dir.mktmpdir('benchmark_')
    system("git clone #{repository_url} #{@temp_dir}")
    
    if branch_name.present? && branch_name != 'main'
      Dir.chdir(@temp_dir) do
        system("git checkout #{branch_name}")
      end
    end
  end
  
  def run_static_analysis
    rubocop_results = analyze_with_rubocop
    reek_results = analyze_with_reek
    
    @benchmark_results << {
      tool: 'rubocop',
      violations: rubocop_results[:violations],
      score: calculate_rubocop_score(rubocop_results)
    }
    
    @benchmark_results << {
      tool: 'reek',
      smells: reek_results[:smells],
      score: calculate_reek_score(reek_results)
    }
  end
  
  def analyze_with_rubocop
    output = `cd #{@temp_dir} && rubocop --format json`
    JSON.parse(output)
  rescue JSON::ParserError
    { violations: [], summary: { offense_count: 0 } }
  end
  
  def analyze_with_reek
    output = `cd #{@temp_dir} && reek --format json`
    JSON.parse(output)
  rescue JSON::ParserError
    { smells: [] }
  end
  
  def generate_complexity_metrics
    flog_score = calculate_flog_complexity
    flay_duplications = detect_code_duplications
    
    @benchmark_results << {
      tool: 'complexity',
      flog_score: flog_score,
      duplications: flay_duplications,
      score: normalize_complexity_score(flog_score, flay_duplications)
    }
  end
  
  def calculate_flog_complexity
    output = `cd #{@temp_dir} && flog --score --methods-only .`
    output.scan(/\d+\.\d+/).first.to_f
  rescue
    0.0
  end
  
  def detect_code_duplications
    output = `cd #{@temp_dir} && flay --diff .`
    output.scan(/\d+ similar lines/).length
  rescue
    0
  end
  
  def create_benchmark_report
    BenchmarkReport.create!(
      user_id: user_id,
      repository_url: repository_url,
      branch_name: branch_name,
      results: @benchmark_results,
      overall_score: calculate_overall_score,
      completed_at: Time.current
    )
  end
  
  def calculate_overall_score
    return 0 if @benchmark_results.empty?
    
    scores = @benchmark_results.map { |result| result[:score] || 0 }
    (scores.sum / scores.length.to_f).round(2)
  end
  
  def finalize_results
    update_user_status('completed')
    @analysis_complete = true
    cleanup_temporary_files
  end
  
  def cleanup_temporary_files
    FileUtils.rm_rf(@temp_dir) if @temp_dir && Dir.exist?(@temp_dir)
  end
  
  def calculate_rubocop_score(results)
    offense_count = results.dig('summary', 'offense_count') || 0
    [100 - (offense_count * 2), 0].max
  end
  
  def calculate_reek_score(results)
    smell_count = results['smells']&.length || 0
    [100 - (smell_count * 3), 0].max
  end
  
  def normalize_complexity_score(flog_score, duplications)
    complexity_penalty = (flog_score / 10.0) + (duplications * 5)
    [100 - complexity_penalty, 0].max.round(2)
  end
  
  def logger
    Rails.logger
  end
end