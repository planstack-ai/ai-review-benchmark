# frozen_string_literal: true

class CounterCacheService
  def initialize(record)
    @record = record
    @model_class = record.class
  end

  def update_counters(association_name, delta = 1)
    return unless counter_cache_enabled?(association_name)

    counter_column = counter_cache_column(association_name)
    parent_record = find_parent_record(association_name)

    return unless parent_record && counter_column

    update_counter_atomically(parent_record, counter_column, delta)
    invalidate_cache_if_needed(parent_record, counter_column)
  end

  def recalculate_counter(association_name)
    return unless counter_cache_enabled?(association_name)

    counter_column = counter_cache_column(association_name)
    parent_record = find_parent_record(association_name)

    return unless parent_record && counter_column

    actual_count = calculate_actual_count(association_name)
    parent_record.update_column(counter_column, actual_count)
    invalidate_cache_if_needed(parent_record, counter_column)
  end

  def batch_update_counters(records, association_name, delta = 1)
    return if records.empty? || !counter_cache_enabled?(association_name)

    counter_column = counter_cache_column(association_name)
    grouped_records = group_records_by_parent(records, association_name)

    grouped_records.each do |parent_id, child_records|
      parent_record = find_parent_by_id(association_name, parent_id)
      next unless parent_record

      total_delta = child_records.size * delta
      update_counter_atomically(parent_record, counter_column, total_delta)
      invalidate_cache_if_needed(parent_record, counter_column)
    end
  end

  private

  def counter_cache_enabled?(association_name)
    reflection = @model_class.reflect_on_association(association_name)
    reflection&.options&.key?(:counter_cache)
  end

  def counter_cache_column(association_name)
    reflection = @model_class.reflect_on_association(association_name)
    counter_cache_option = reflection&.options&.dig(:counter_cache)

    case counter_cache_option
    when true
      "#{@model_class.name.underscore.pluralize}_count"
    when String, Symbol
      counter_cache_option.to_s
    else
      nil
    end
  end

  def find_parent_record(association_name)
    @record.send(association_name) if @record.respond_to?(association_name)
  end

  def find_parent_by_id(association_name, parent_id)
    reflection = @model_class.reflect_on_association(association_name)
    reflection.klass.find_by(id: parent_id)
  end

  def update_counter_atomically(parent_record, counter_column, delta)
    parent_record.class.where(id: parent_record.id)
                       .update_all("#{counter_column} = #{counter_column} + #{delta}")
  end

  def calculate_actual_count(association_name)
    parent_record = find_parent_record(association_name)
    return 0 unless parent_record

    inverse_association = find_inverse_association(association_name)
    return 0 unless inverse_association

    parent_record.send(inverse_association).count
  end

  def find_inverse_association(association_name)
    reflection = @model_class.reflect_on_association(association_name)
    reflection&.inverse_of&.name
  end

  def group_records_by_parent(records, association_name)
    foreign_key = @model_class.reflect_on_association(association_name).foreign_key
    records.group_by { |record| record.send(foreign_key) }
  end

  def invalidate_cache_if_needed(parent_record, counter_column)
    cache_key = "#{parent_record.class.name.underscore}/#{parent_record.id}/#{counter_column}"
    Rails.cache.delete(cache_key) if defined?(Rails.cache)
  end
end