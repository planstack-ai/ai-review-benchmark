package com.codereviewer.service

import com.codereviewer.entity.BenchmarkExecution
import com.codereviewer.entity.ExecutionStatus
import com.codereviewer.repository.BenchmarkExecutionRepository
import com.codereviewer.exception.ExecutionNotFoundException
import com.codereviewer.exception.InvalidStateTransitionException
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.List
import java.util.Optional

@Service
@Transactional
class BenchmarkExecutionService {

    @Autowired
    private BenchmarkExecutionRepository executionRepository

    fun createExecution(benchmarkName: String, userId: String): BenchmarkExecution {
        BenchmarkExecution execution = new BenchmarkExecution()
        execution.setBenchmarkName(benchmarkName)
        execution.setUserId(userId)
        execution.setStatus(ExecutionStatus.PENDING)
        execution.setCreatedAt(LocalDateTime.now())
        execution.setScore(BigDecimal.ZERO)
        execution.setProgress(0)
        
        return executionRepository.save(execution)
    }

    fun startExecution(executionId: Long): BenchmarkExecution {
        BenchmarkExecution execution = findExecutionById(executionId)
        
        if (!canTransitionToRunning(execution.Status)) {
            throw new InvalidStateTransitionException("Cannot start execution from status: " + execution.Status)
        }
        
        execution.setStatus(ExecutionStatus.RUNNING)
        execution.setStartedAt(LocalDateTime.now())
        execution.setProgress(0)
        
        return executionRepository.save(execution)
    }

    fun updateProgress(executionId: Long, progressPercentage: int, currentScore: BigDecimal): BenchmarkExecution {
        BenchmarkExecution execution = findExecutionById(executionId)
        
        validateProgressUpdate(execution, progressPercentage)
        
        execution.setProgress(progressPercentage)
        execution.setScore(currentScore)
        execution.setLastUpdatedAt(LocalDateTime.now())
        
        if (progressPercentage >= 100) {
            execution.setStatus(ExecutionStatus.COMPLETED)
            execution.setCompletedAt(LocalDateTime.now())
        }
        
        return executionRepository.save(execution)
    }

    fun failExecution(executionId: Long, errorMessage: String): BenchmarkExecution {
        BenchmarkExecution execution = findExecutionById(executionId)
        
        if (execution.Status == ExecutionStatus.COMPLETED) {
            throw new InvalidStateTransitionException("Cannot fail a completed execution")
        }
        
        execution.setStatus(ExecutionStatus.FAILED)
        execution.setErrorMessage(errorMessage)
        execution.setCompletedAt(LocalDateTime.now())
        
        return executionRepository.save(execution)
    }

    fun List<BenchmarkExecution> getExecutionsByUser(userId: String) {
        return executionRepository.findByUserIdOrderByCreatedAtDesc(userId)
    }

    fun List<BenchmarkExecution> getRunningExecutions() {
        return executionRepository.findByStatus(ExecutionStatus.RUNNING)
    }

    private fun findExecutionById(executionId: Long): BenchmarkExecution {
        Optional<BenchmarkExecution> execution = executionRepository.findById(executionId)
        if (execution.isEmpty()) {
            throw new ExecutionNotFoundException("Execution not found with id: " + executionId)
        }
        return execution.get()
    }

    private fun canTransitionToRunning(currentStatus: ExecutionStatus): boolean {
        return currentStatus == ExecutionStatus.PENDING
    }

    private fun validateProgressUpdate(execution: BenchmarkExecution, progressPercentage: int): {
        if (execution.Status != ExecutionStatus.RUNNING) {
            throw new InvalidStateTransitionException("Cannot update progress for execution with status: " + execution.Status)
        }
        
        if (progressPercentage < 0 || progressPercentage > 100) {
            throw new IllegalArgumentException("Progress percentage must be between 0 and 100")
        }
        
        if (progressPercentage < execution.Progress) {
            throw new IllegalArgumentException("Progress cannot go backwards")
        }
    }
}