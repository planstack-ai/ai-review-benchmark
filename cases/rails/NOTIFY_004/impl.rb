# frozen_string_literal: true

class EmailTemplateService
  attr_reader :template, :user, :context

  def initialize(template, user, context = {})
    @template = template
    @user = user
    @context = context
  end

  def render
    return nil unless template&.content.present?

    processed_content = substitute_variables(template.content)
    validate_required_fields(processed_content)
    processed_content
  end

  def preview
    render
  end

  def send_email
    rendered_content = render
    return false unless rendered_content

    EmailDeliveryJob.perform_later(
      to: user.email,
      subject: substitute_variables(template.subject),
      body: rendered_content
    )
    true
  end

  private

  def substitute_variables(content)
    return content unless content.is_a?(String)

    content.gsub(/\{\{(\w+(?:\.\w+)*)\}\}/) do |match|
      variable_path = Regexp.last_match(1)
      resolve_variable(variable_path)
    end
  end

  def resolve_variable(path)
    parts = path.split('.')
    current_value = context

    parts.each do |part|
      case part
      when 'user'
        current_value = user
      when 'name'
        current_value = current_value.name
      when 'email'
        current_value = current_value&.email
      when 'company'
        current_value = context[:company] || user&.company
      when 'date'
        current_value = Date.current.strftime('%B %d, %Y')
      else
        current_value = context[part.to_sym] || context[part]
      end
    end

    current_value.to_s
  end

  def validate_required_fields(content)
    required_patterns = [
      /\{\{user\.email\}\}/,
      /\{\{user\.name\}\}/
    ]

    required_patterns.each do |pattern|
      if content.match?(pattern)
        raise TemplateValidationError, "Required template variable not resolved: #{pattern.source}"
      end
    end
  end

  def default_context
    {
      company: 'Our Company',
      support_email: 'support@example.com',
      year: Date.current.year
    }
  end
end

class TemplateValidationError < StandardError; end