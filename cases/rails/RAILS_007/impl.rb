# frozen_string_literal: true

class RaceService
  class RaceCreationError < StandardError; end

  def initialize(race_params)
    @race_params = race_params.with_indifferent_access
    @name = @race_params[:name]
    @date = @race_params[:date]
    @location = @race_params[:location]
  end

  def find_or_create_race
    validate_params!
    
    existing_race = find_existing_race
    return existing_race if existing_race

    create_new_race
  end

  private

  attr_reader :race_params, :name, :date, :location

  def validate_params!
    raise RaceCreationError, "Name is required" if name.blank?
    raise RaceCreationError, "Date is required" if date.blank?
    raise RaceCreationError, "Location is required" if location.blank?
    raise RaceCreationError, "Invalid date format" unless valid_date?
  end

  def valid_date?
    Date.parse(date.to_s)
    true
  rescue ArgumentError
    false
  end

  def find_existing_race
    Race.find_by(
      name: normalized_name,
      date: parsed_date,
      location: normalized_location
    )
  end

  def create_new_race
    race_attributes = build_race_attributes
    
    Race.create!(race_attributes).tap do |race|
      log_race_creation(race)
      notify_race_created(race)
    end
  rescue ActiveRecord::RecordInvalid => e
    raise RaceCreationError, "Failed to create race: #{e.message}"
  end

  def build_race_attributes
    {
      name: normalized_name,
      date: parsed_date,
      location: normalized_location,
      status: 'scheduled',
      max_participants: race_params[:max_participants] || 100,
      registration_fee: race_params[:registration_fee] || 0.0,
      description: race_params[:description]
    }
  end

  def normalized_name
    @normalized_name ||= name.strip.titleize
  end

  def normalized_location
    @normalized_location ||= location.strip.titleize
  end

  def parsed_date
    @parsed_date ||= Date.parse(date.to_s)
  end

  def log_race_creation(race)
    Rails.logger.info "Created new race: #{race.name} on #{race.date} at #{race.location}"
  end

  def notify_race_created(race)
    RaceCreatedNotificationJob.perform_later(race.id)
  end
end