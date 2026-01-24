# 既存コードベース情報

## ExamResult モデル

```ruby
class ExamResult < ApplicationRecord
  belongs_to :exam
  belongs_to :student

  validates :score, presence: true, numericality: { in: 0..100 }

  scope :for_exam, ->(exam_id) { where(exam_id: exam_id) }
  scope :ordered_by_score, -> { order(score: :desc) }
end
```

## スキーマ

```ruby
create_table "exam_results", force: :cascade do |t|
  t.bigint "exam_id", null: false
  t.bigint "student_id", null: false
  t.integer "score", null: false
  t.datetime "created_at", null: false
  t.datetime "updated_at", null: false
  t.index ["exam_id"], name: "index_exam_results_on_exam_id"
  t.index ["student_id"], name: "index_exam_results_on_student_id"
end
```
