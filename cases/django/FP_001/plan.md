# Task Management System - Standard CRUD Operations

## Overview

A web-based task management system that allows users to create, read, update, and delete tasks. The system provides a simple interface for managing personal or team tasks with basic information tracking including task titles, descriptions, status, and timestamps.

## Requirements

1. Implement a Task model with fields for title, description, status, creation date, and last modified date
2. Create a list view that displays all tasks with pagination support
3. Implement a detail view to show individual task information
4. Provide a create view with a form to add new tasks
5. Build an update view allowing modification of existing tasks
6. Include a delete view with confirmation before removal
7. Use Django's built-in generic class-based views where appropriate
8. Implement proper URL routing for all CRUD operations
9. Create HTML templates for each view with consistent styling
10. Add form validation to ensure required fields are populated
11. Include success messages after create, update, and delete operations
12. Implement proper error handling for invalid requests
13. Use Django's CSRF protection for all forms
14. Follow Django naming conventions for URLs, views, and templates

## Constraints

1. Task titles must be between 1 and 200 characters
2. Task descriptions are optional but limited to 1000 characters when provided
3. Status field must be one of: "pending", "in_progress", "completed"
4. Creation and modification timestamps should be automatically managed
5. All forms must include proper validation error display
6. Delete operations require explicit user confirmation
7. List view should display maximum 10 tasks per page
8. All views must handle both GET and POST requests appropriately

## References

See context.md for existing codebase structure and related implementations.