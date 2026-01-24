# frozen_string_literal: true

class ProjectAnalyticsService
  def initialize(user)
    @user = user
    @projects = user.projects.includes(:tasks, :team_members, comments: :author)
  end

  def generate_report
    {
      project_summaries: build_project_summaries,
      team_performance: calculate_team_performance,
      completion_metrics: analyze_completion_metrics,
      recent_activity: fetch_recent_activity
    }
  end

  def export_detailed_data
    projects_with_associations.map do |project|
      {
        id: project.id,
        name: project.name,
        task_count: project.tasks.size,
        completed_tasks: project.tasks.select(&:completed?).size,
        team_size: project.team_members.size,
        recent_comments: project.comments.limit(10).map(&:content),
        member_names: project.team_members.map(&:full_name)
      }
    end
  end

  def calculate_productivity_scores
    productivity_data = {}
    
    projects_with_associations.each do |project|
      total_tasks = project.tasks.size
      completed_tasks = project.tasks.count(&:completed?)
      active_members = project.team_members.select(&:active?)
      
      productivity_data[project.id] = {
        completion_rate: calculate_completion_rate(completed_tasks, total_tasks),
        member_efficiency: calculate_member_efficiency(active_members, completed_tasks),
        comment_engagement: project.comments.group_by(&:author).transform_values(&:size)
      }
    end
    
    productivity_data
  end

  private

  def projects_with_associations
    @projects
  end

  def build_project_summaries
    projects_with_associations.map do |project|
      {
        name: project.name,
        status: determine_project_status(project),
        progress: calculate_project_progress(project),
        team_count: project.team_members.size
      }
    end
  end

  def calculate_team_performance
    team_stats = {}
    
    projects_with_associations.each do |project|
      project.team_members.each do |member|
        team_stats[member.id] ||= { projects: 0, total_comments: 0 }
        team_stats[member.id][:projects] += 1
        team_stats[member.id][:total_comments] += project.comments.count { |c| c.author_id == member.id }
      end
    end
    
    team_stats
  end

  def analyze_completion_metrics
    total_tasks = projects_with_associations.sum { |p| p.tasks.size }
    completed_tasks = projects_with_associations.sum { |p| p.tasks.count(&:completed?) }
    
    {
      total_tasks: total_tasks,
      completed_tasks: completed_tasks,
      completion_percentage: calculate_completion_rate(completed_tasks, total_tasks)
    }
  end

  def fetch_recent_activity
    projects_with_associations.flat_map(&:comments)
                             .sort_by(&:created_at)
                             .last(20)
                             .map { |comment| format_comment_activity(comment) }
  end

  def determine_project_status(project)
    completed_ratio = project.tasks.count(&:completed?).to_f / project.tasks.size
    return 'completed' if completed_ratio >= 1.0
    return 'in_progress' if completed_ratio >= 0.1
    'not_started'
  end

  def calculate_project_progress(project)
    return 0 if project.tasks.empty?
    (project.tasks.count(&:completed?).to_f / project.tasks.size * 100).round(2)
  end

  def calculate_completion_rate(completed, total)
    return 0 if total.zero?
    (completed.to_f / total * 100).round(2)
  end

  def calculate_member_efficiency(members, completed_tasks)
    return 0 if members.empty?
    completed_tasks.to_f / members.size
  end

  def format_comment_activity(comment)
    {
      author: comment.author.full_name,
      content: comment.content.truncate(100),
      created_at: comment.created_at
    }
  end
end