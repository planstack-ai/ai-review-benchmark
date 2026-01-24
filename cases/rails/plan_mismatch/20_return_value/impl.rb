# frozen_string_literal: true

class DataImportService
  def initialize(file)
    @file = file
  end

  def execute
    rows = CsvParser.parse(@file)
    success_count = 0
    failed_count = 0

    rows.each do |row|
      if create_product(row)
        success_count += 1
      else
        failed_count += 1
      end
    end

    # BUG: 配列で返しているが、ハッシュで返すべき
    [success_count, failed_count]
  end

  private

  def create_product(row)
    Product.create(name: row["name"], price: row["price"])&.persisted?
  end
end
