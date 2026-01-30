package com.codereviewer.service;

import com.codereviewer.entity.BenchmarkExecution;
import com.codereviewer.entity.ExecutionStatus;
import com.codereviewer.repository.BenchmarkExecutionRepository;
import com.codereviewer.exception.ExecutionNotFoundException;
import com.codereviewer.exception.InvalidStateTransitionException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class BenchmarkExecutionService {

    @Autowired
    private BenchmarkExecutionRepository executionRepository;

    public BenchmarkExecution createExecution(String benchmarkName, String userId) {
        BenchmarkExecution execution = new BenchmarkExecution();
        execution.setBenchmarkName(benchmarkName);
        execution.setUserId(userId);
        execution.setStatus(ExecutionStatus.PENDING);
        execution.setCreatedAt(LocalDateTime.now());
        execution.setScore(BigDecimal.ZERO);
        execution.setProgress(0);
        
        return executionRepository.save(execution);
    }

    public BenchmarkExecution startExecution(Long executionId) {
        BenchmarkExecution execution = findExecutionById(executionId);
        
        if (!canTransitionToRunning(execution.getStatus())) {
            throw new InvalidStateTransitionException("Cannot start execution from status: " + execution.getStatus());
        }
        
        execution.setStatus(ExecutionStatus.RUNNING);
        execution.setStartedAt(LocalDateTime.now());
        execution.setProgress(0);
        
        return executionRepository.save(execution);
    }

    public BenchmarkExecution updateProgress(Long executionId, int progressPercentage, BigDecimal currentScore) {
        BenchmarkExecution execution = findExecutionById(executionId);
        
        validateProgressUpdate(execution, progressPercentage);
        
        execution.setProgress(progressPercentage);
        execution.setScore(currentScore);
        execution.setLastUpdatedAt(LocalDateTime.now());
        
        if (progressPercentage >= 100) {
            execution.setStatus(ExecutionStatus.COMPLETED);
            execution.setCompletedAt(LocalDateTime.now());
        }
        
        return executionRepository.save(execution);
    }

    public BenchmarkExecution failExecution(Long executionId, String errorMessage) {
        BenchmarkExecution execution = findExecutionById(executionId);
        
        if (execution.getStatus() == ExecutionStatus.COMPLETED) {
            throw new InvalidStateTransitionException("Cannot fail a completed execution");
        }
        
        execution.setStatus(ExecutionStatus.FAILED);
        execution.setErrorMessage(errorMessage);
        execution.setCompletedAt(LocalDateTime.now());
        
        return executionRepository.save(execution);
    }

    public List<BenchmarkExecution> getExecutionsByUser(String userId) {
        return executionRepository.findByUserIdOrderByCreatedAtDesc(userId);
    }

    public List<BenchmarkExecution> getRunningExecutions() {
        return executionRepository.findByStatus(ExecutionStatus.RUNNING);
    }

    private BenchmarkExecution findExecutionById(Long executionId) {
        Optional<BenchmarkExecution> execution = executionRepository.findById(executionId);
        if (execution.isEmpty()) {
            throw new ExecutionNotFoundException("Execution not found with id: " + executionId);
        }
        return execution.get();
    }

    private boolean canTransitionToRunning(ExecutionStatus currentStatus) {
        return currentStatus == ExecutionStatus.PENDING;
    }

    private void validateProgressUpdate(BenchmarkExecution execution, int progressPercentage) {
        if (execution.getStatus() != ExecutionStatus.RUNNING) {
            throw new InvalidStateTransitionException("Cannot update progress for execution with status: " + execution.getStatus());
        }
        
        if (progressPercentage < 0 || progressPercentage > 100) {
            throw new IllegalArgumentException("Progress percentage must be between 0 and 100");
        }
        
        if (progressPercentage < execution.getProgress()) {
            throw new IllegalArgumentException("Progress cannot go backwards");
        }
    }
}