package com.example.benchmark.service

import com.example.benchmark.entity.CodeReviewTask
import com.example.benchmark.entity.TaskStatus
import com.example.benchmark.repository.CodeReviewTaskRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.*

@Service
@Transactional
class CodeReviewBenchmarkService(
    private val taskRepository: CodeReviewTaskRepository
) {

    fun createReviewTask(
        repositoryUrl: String,
        complexity: String,
        estimatedHours: BigDecimal
    ): CodeReviewTask {
        val task = CodeReviewTask(
            id = UUID.randomUUID(),
            repositoryUrl = repositoryUrl,
            complexity = complexity,
            estimatedHours = estimatedHours,
            status = TaskStatus.PENDING,
            createdAt = LocalDateTime.now()
        )
        return taskRepository.save(task)
    }

    fun assignReviewer(taskId: UUID, reviewerId: UUID): CodeReviewTask? {
        return taskRepository.findById(taskId)?.let { task ->
            if (task.status == TaskStatus.PENDING) {
                val updatedTask = task.copy(
                    reviewerId = reviewerId,
                    status = TaskStatus.IN_PROGRESS,
                    assignedAt = LocalDateTime.now()
                )
                taskRepository.save(updatedTask)
            } else {
                throw IllegalStateException("Task ${task.id} is not available for assignment")
            }
        }
    }

    fun submitReview(taskId: UUID, score: Int, feedback: String): CodeReviewTask? {
        return taskRepository.findById(taskId)?.let { task ->
            validateReviewSubmission(task, score)
            
            val completedTask = task.copy(
                status = TaskStatus.COMPLETED,
                reviewScore = score,
                reviewFeedback = feedback,
                completedAt = LocalDateTime.now(),
                actualHours = calculateActualHours(task)
            )
            taskRepository.save(completedTask)
        }
    }

    fun updateTaskPriority(taskId: UUID, newPriority: Int): CodeReviewTask? {
        return taskRepository.findById(taskId)?.let { task ->
            if (task.status != TaskStatus.COMPLETED) {
                val updatedTask = task.copy(
                    priority = newPriority,
                    lastModified = LocalDateTime.now()
                )
                taskRepository.save(updatedTask)
            } else {
                task
            }
        }
    }

    fun cancelTask(taskId: UUID): CodeReviewTask? {
        return taskRepository.findById(taskId)?.let { task ->
            if (task.status in listOf(TaskStatus.PENDING, TaskStatus.IN_PROGRESS)) {
                val cancelledTask = task.copy(
                    status = TaskStatus.CANCELLED,
                    cancelledAt = LocalDateTime.now()
                )
                taskRepository.save(cancelledTask)
            } else {
                throw IllegalStateException("Cannot cancel task in ${task.status} status")
            }
        }
    }

    private fun validateReviewSubmission(task: CodeReviewTask, score: Int) {
        require(task.status == TaskStatus.IN_PROGRESS) {
            "Task must be in progress to submit review"
        }
        require(score in 1..10) {
            "Review score must be between 1 and 10"
        }
        require(task.reviewerId != null) {
            "Task must have an assigned reviewer"
        }
    }

    private fun calculateActualHours(task: CodeReviewTask): BigDecimal? {
        return task.assignedAt?.let { assigned ->
            val hoursWorked = java.time.Duration.between(assigned, LocalDateTime.now()).toHours()
            BigDecimal.valueOf(hoursWorked)
        }
    }

    fun getTasksByStatus(status: TaskStatus): List<CodeReviewTask> {
        return taskRepository.findByStatus(status)
    }

    fun getTaskStatistics(): Map<String, Any> {
        val allTasks = taskRepository.findAll()
        return mapOf(
            "totalTasks" to allTasks.size,
            "completedTasks" to allTasks.count { it.status == TaskStatus.COMPLETED },
            "averageScore" to calculateAverageScore(allTasks),
            "averageCompletionTime" to calculateAverageCompletionTime(allTasks)
        )
    }

    private fun calculateAverageScore(tasks: List<CodeReviewTask>): BigDecimal {
        val completedTasks = tasks.filter { it.status == TaskStatus.COMPLETED && it.reviewScore != null }
        return if (completedTasks.isNotEmpty()) {
            BigDecimal.valueOf(completedTasks.mapNotNull { it.reviewScore }.average())
        } else {
            BigDecimal.ZERO
        }
    }

    private fun calculateAverageCompletionTime(tasks: List<CodeReviewTask>): BigDecimal {
        val completedTasks = tasks.filter { it.actualHours != null }
        return if (completedTasks.isNotEmpty()) {
            completedTasks.mapNotNull { it.actualHours }
                .fold(BigDecimal.ZERO) { acc, hours -> acc.add(hours) }
                .divide(BigDecimal.valueOf(completedTasks.size.toLong()))
        } else {
            BigDecimal.ZERO
        }
    }
}