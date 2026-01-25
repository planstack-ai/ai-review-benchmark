# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: repositories
#
#  id         :bigint           not null, primary key
#  name       :string           not null
#  url        :string
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_repositories_on_name  (name) UNIQUE
#

# Table name: code_files
#
#  id            :bigint           not null, primary key
#  repository_id :bigint           not null
#  path          :string           not null
#  file_size     :integer          default(0)
#  active        :boolean          default(true)
#  created_at    :datetime         not null
#  updated_at    :datetime         not null
#
# Indexes
#
#  index_code_files_on_repository_id  (repository_id)
#  index_code_files_on_active         (active)
#

# Table name: benchmarks
#
#  id             :bigint           not null, primary key
#  repository_id  :bigint           not null
#  benchmark_type :string           not null
#  total_files    :integer          default(0)
#  average_score  :decimal(5,2)
#  total_issues   :integer          default(0)
#  status         :string           default("pending")
#  created_at     :datetime         not null
#  updated_at     :datetime         not null
#
# Indexes
#
#  index_benchmarks_on_repository_id  (repository_id)
#  index_benchmarks_on_benchmark_type (benchmark_type)
#

# Table name: benchmark_results
#
#  id           :bigint           not null, primary key
#  benchmark_id :bigint           not null
#  file_id      :bigint           not null
#  score        :decimal(5,2)
#  issues_data  :jsonb            default([])
#  completed_at :datetime
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Indexes
#
#  index_benchmark_results_on_benchmark_id  (benchmark_id)
#  index_benchmark_results_on_file_id       (file_id)
#
```

## Models

```ruby
class Repository < ApplicationRecord
  has_many :code_files, dependent: :destroy
  has_many :benchmarks, dependent: :destroy

  validates :name, presence: true, uniqueness: true
end

class CodeFile < ApplicationRecord
  belongs_to :repository

  validates :path, presence: true

  scope :active, -> { where(active: true) }
  scope :small, -> { where('file_size < ?', 1.megabyte) }
end

class Benchmark < ApplicationRecord
  TYPES = %w[performance security maintainability].freeze
  STATUSES = %w[pending running completed failed].freeze

  belongs_to :repository
  has_many :benchmark_results, dependent: :destroy

  validates :benchmark_type, inclusion: { in: TYPES }
  validates :status, inclusion: { in: STATUSES }
end

class BenchmarkResult < ApplicationRecord
  belongs_to :benchmark
  belongs_to :file, class_name: 'CodeFile', foreign_key: :file_id

  validates :score, presence: true, numericality: { greater_than_or_equal_to: 0 }
end
```

## Analyzers

```ruby
class PerformanceAnalyzer
  def initialize(file)
    @file = file
  end

  def calculate_score
    # Returns score 0-100 based on performance metrics
  end

  def detect_issues
    # Returns array of performance issues found
  end
end

class SecurityAnalyzer
  def initialize(file)
    @file = file
  end

  def calculate_score
    # Returns score 0-100 based on security checks
  end

  def detect_issues
    # Returns array of security vulnerabilities found
  end
end

class MaintainabilityAnalyzer
  def initialize(file)
    @file = file
  end

  def calculate_score
    # Returns score 0-100 based on code maintainability
  end

  def detect_issues
    # Returns array of maintainability concerns found
  end
end
```
