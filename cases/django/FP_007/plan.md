# Complex Callback Chain Signal Processing System

## Overview

This system implements a multi-stage document processing workflow using Django signals to coordinate between different processing stages. The system handles document uploads, validation, content analysis, and notification delivery through a chain of signal handlers that must execute in a specific sequence to maintain data integrity and proper workflow execution.

## Requirements

1. Create a Document model with fields for title, content, status, and processing metadata
2. Implement a DocumentProcessor class that handles the core processing logic
3. Create signal handlers for pre_save, post_save, and custom signals that form a processing chain
4. Ensure signals fire in the correct order: validation → processing → notification
5. Implement proper signal disconnection and reconnection for testing scenarios
6. Create custom signals for document_validated, document_processed, and notification_sent
7. Handle signal propagation correctly to prevent infinite loops or missed signals
8. Implement proper error handling within signal handlers without breaking the chain
9. Create a management command that can trigger the full processing workflow
10. Ensure all signal handlers are properly registered and discoverable by Django
11. Implement logging at each stage of the signal chain for debugging purposes
12. Create unit tests that verify the complete signal chain executes correctly

## Constraints

1. Signal handlers must not modify the same model instance simultaneously
2. Each signal handler must complete successfully before the next stage begins
3. The system must handle cases where intermediate signals fail gracefully
4. Signal handlers must be idempotent to handle potential retry scenarios
5. The processing chain must maintain transactional integrity across all stages
6. Custom signals must include proper sender identification and signal data
7. Signal handlers must not create circular dependencies between processing stages

## References

See context.md for existing signal handling patterns and Django signal best practices used in the current codebase.