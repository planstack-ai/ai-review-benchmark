# frozen_string_literal: true

class TopScoreService
  def initialize(exam_id)
    @exam_id = exam_id
  end

  def find_top_score
    results = ExamResult.for_exam(@exam_id).ordered_by_score

    # BUG: first は空配列でも nil を返すが、その後の .score で NoMethodError
    # results.first が nil の場合のチェックがない
    results.first.score
  end

  def find_top_scorer
    results = ExamResult.for_exam(@exam_id).ordered_by_score

    # BUG: 同様に空の場合に .student で NoMethodError
    results.first.student
  end
end
