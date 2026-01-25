# Support Ticket Workflow

## Overview

Manage customer support ticket lifecycle.

## Requirements

1. Customers create tickets in open state
2. Agents work on tickets (in_progress)
3. Agents can request info from customer (waiting_customer)
4. Tickets resolved or escalated as needed
5. Customers can reopen resolved tickets

## Valid States

- open → in_progress (agent starts working)
- open → closed (duplicate/spam)
- in_progress → waiting_customer (need more info)
- in_progress → resolved (issue fixed)
- in_progress → escalated (needs manager)
- waiting_customer → in_progress (customer replied)
- resolved → reopened (customer not satisfied)
- escalated → in_progress (manager assigns back)
