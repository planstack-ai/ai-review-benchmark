# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: documents
#
#  id                :bigint           not null, primary key
#  title             :string           not null
#  raw_content       :text             not null
#  processed_content :text
#  metadata          :jsonb            default({})
#  status            :string           default("pending"), not null
#  user_id           :bigint           not null
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
#
# Indexes
#
#  index_documents_on_user_id  (user_id)
#  index_documents_on_status   (status)
```

## Models

```ruby
class Document < ApplicationRecord
  STATUSES = %w[pending processing processed failed].freeze

  belongs_to :user

  validates :title, presence: true
  validates :raw_content, presence: true
  validates :status, inclusion: { in: STATUSES }

  scope :pending, -> { where(status: 'pending') }
  scope :processed, -> { where(status: 'processed') }
  scope :failed, -> { where(status: 'failed') }
end

class User < ApplicationRecord
  has_many :documents, dependent: :destroy

  validates :email, presence: true, uniqueness: true
  validates :name, presence: true
end
```

## Service Pattern Guidelines

When implementing services with ActiveModel::Callbacks:
- Use `throw :abort` in before_* callbacks to halt the callback chain when validation fails
- Validation callbacks should run first and prevent further processing on failure
- Consider callback execution order carefully when callbacks have dependencies
- Use `prepend: true` option to ensure critical callbacks run before others
- Callbacks that fail validation should prevent the callback chain from continuing

## Usage Guidelines

- Be mindful of callback execution order. Callbacks in the same phase execute in the order they are defined. Ensure proper sequencing of operations.

- Be aware that `update_all` and `delete_all` skip callbacks and validations. Use them only when you intentionally want to bypass model logic.

