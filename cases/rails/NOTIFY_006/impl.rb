# frozen_string_literal: true

class BulkEmailService
  include ActiveModel::Validations

  attr_reader :campaign, :recipients, :errors

  validates :campaign, presence: true
  validates :recipients, presence: true

  def initialize(campaign:, recipients:)
    @campaign = campaign
    @recipients = recipients
    @errors = []
  end

  def execute
    return false unless valid?

    begin
      prepare_email_content
      send_bulk_emails
      update_campaign_metrics
      true
    rescue StandardError => e
      @errors << "Failed to send bulk emails: #{e.message}"
      Rails.logger.error("BulkEmailService error: #{e.message}")
      false
    end
  end

  private

  def prepare_email_content
    @email_template = campaign.email_template
    @subject = personalize_subject(campaign.subject)
    @sender_email = campaign.sender_email || Rails.application.config.default_sender_email
  end

  def send_bulk_emails
    successful_sends = 0
    failed_sends = 0

    recipients.each do |recipient|
      if send_email_to_recipient(recipient)
        successful_sends += 1
      else
        failed_sends += 1
      end
    end

    log_send_results(successful_sends, failed_sends)
  end

  def send_email_to_recipient(recipient)
    return false unless recipient.email.present? && recipient.subscribed?

    personalized_content = personalize_content(recipient)
    
    BulkEmailMailer.campaign_email(
      recipient: recipient,
      subject: @subject,
      content: personalized_content,
      sender: @sender_email,
      campaign_id: campaign.id
    ).deliver_now

    track_email_sent(recipient)
    true
  rescue Net::SMTPError, StandardError => e
    Rails.logger.warn("Failed to send email to #{recipient.email}: #{e.message}")
    false
  end

  def personalize_content(recipient)
    content = @email_template.dup
    content.gsub!('{{first_name}}', recipient.first_name || 'Valued Customer')
    content.gsub!('{{last_name}}', recipient.last_name || '')
    content.gsub!('{{company}}', recipient.company || '')
    content
  end

  def personalize_subject(subject)
    return subject unless campaign.personalize_subject?
    "#{subject} - Exclusive for #{campaign.target_segment.capitalize}"
  end

  def track_email_sent(recipient)
    EmailDelivery.create!(
      campaign: campaign,
      recipient: recipient,
      sent_at: Time.current,
      status: 'sent'
    )
  end

  def update_campaign_metrics
    campaign.increment!(:emails_sent, recipients.count)
    campaign.update!(last_sent_at: Time.current)
  end

  def log_send_results(successful, failed)
    Rails.logger.info("Bulk email campaign #{campaign.id} completed: #{successful} sent, #{failed} failed")
  end
end