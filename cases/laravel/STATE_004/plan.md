# Content Publishing Workflow

## Overview

Manage article publishing lifecycle with review process.

## Requirements

1. Draft articles go through review before publishing
2. Reviewers can approve or request changes
3. Only approved articles can be published
4. Published articles can be unpublished or archived

## Valid States

- draft → pending_review (author submits)
- pending_review → approved (reviewer approves)
- pending_review → draft (reviewer requests changes)
- approved → published (editor publishes)
- published → unpublished (taken down temporarily)
- published → archived (permanently archived)
- unpublished → published (republished)
