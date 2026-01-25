# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: users
#
#  id         :bigint           not null, primary key
#  email      :string           not null
#  name       :string
#  company    :string
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: email_templates
#
#  id           :bigint           not null, primary key
#  key          :string           not null, index: true
#  subject      :string           not null
#  content      :text             not null
#  variables    :json
#  active       :boolean          default: true
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  validates :email, presence: true, format: { with: URI::MailTo::EMAIL_REGEXP }

  def display_name
    name.presence || email.split('@').first
  end
end

class EmailTemplate < ApplicationRecord
  validates :key, presence: true, uniqueness: true
  validates :subject, :content, presence: true

  scope :active, -> { where(active: true) }

  WELCOME_EMAIL = 'welcome_email'.freeze
  PASSWORD_RESET = 'password_reset'.freeze
  ORDER_CONFIRMATION = 'order_confirmation'.freeze

  def variable_names
    variables&.map(&:to_s) || []
  end
end
```

## Jobs

```ruby
class EmailDeliveryJob < ApplicationJob
  queue_as :mailers

  def perform(to:, subject:, body:)
    # Deliver email using configured mail service
    ActionMailer::Base.mail(
      to: to,
      subject: subject,
      body: body
    ).deliver_now
  end
end
```

## Template Variable Syntax

Email templates support variable substitution using `{{variable.path}}` syntax:
- `{{user.name}}` - User's name
- `{{user.email}}` - User's email address
- `{{company}}` - Company name
- `{{date}}` - Current date formatted

## Guidelines for Variable Resolution

When resolving template variables:
- Use safe navigation (`&.`) consistently for all attribute access
- Provide meaningful fallback values for missing data
- Validate that all required variables are resolved before sending
