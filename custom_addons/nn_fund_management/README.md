# NN Fund Management

A production-ready Odoo 18 Community module for managing organisational fund accounts, approvals and spending workflows.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Quick Start (Docker)](#quick-start-docker)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Workflow](#usage-workflow)
- [Architecture](#architecture)
- [Testing](#testing)
- [Reports](#reports)
- [Development & Contributions](#development--contributions)
- [Notes](#notes)

## Overview

This module provides:

- Bank and cash fund accounts with computed balances (received, available, held, assigned).
- Incoming fund posting with per-account duplicate transaction reference protection.
- Approval-driven allocation, requisition and transfer workflows with GM/MD approvers.
- Project and expense head budgets with allocation, reservation and spending controls.
- Partial billing, over-billing prevention and bill reversal support.
- Dashboard views and PDF reports for finance oversight.

## Key Features

- Multi-stage approval flows: Draft → GM Approval → MD Approval → Approved / Rejected / Cancelled
- Reusable approval engine used across allocations, requisitions and transfers
- Configurable approvers and security groups to prevent self-approval
- Activity / chatter integration and approval audit history
- Automated tests covering balances, workflow rules and security

## Quick Start (Docker)

From the project root, start the stack:

```bash
docker compose up -d
```

Open Odoo at:

http://localhost:8069

The stack includes Odoo 18 and PostgreSQL 16. The `custom_addons` directory is mounted into the container at `/mnt/extra-addons`.

## Installation

1. Start the Docker stack.
2. Create a new database or open an existing one.
3. Enable Developer Mode in Odoo.
4. Update the Apps List and search for "NN Fund Management".
5. Install the module.

## Configuration

Navigate to Fund Management → Configuration → Approval Configuration and set:

- Allocation Approval approvers
- Requisition Approval approvers
- Transfer Approval approvers

Assign users to security groups as needed: Fund User, Finance User, GM Approver, MD Approver, Fund Administrator.

## Usage Workflow

Typical flow:

1. Create Fund Accounts.
2. Post Incoming Funds (Finance User).
3. Create Projects and Expense Heads and allocate budgets.
4. Submit Fund Allocations (Requester).
5. Approve allocations: first GM, then MD.
6. Create Requisitions against approved balances.
7. Post partial Bills against requisitions; handle reversals if necessary.
8. Transfer balances between projects/expense heads when required.
9. Monitor balances and reports from the Dashboard.

## Architecture

Core modules and responsibility:

- `models/fund_account.py` — Fund accounts and computed balances
- `models/incoming_fund.py` — Incoming receipts and reference uniqueness
- `models/approval_mixin.py` — Reusable approval and activity engine
- `models/approval.py` — Approval configuration and audit history
- `models/fund_allocation.py` — Allocation workflow and balance reservation
- `models/fund_project.py` — Project balances and aggregates
- `models/expense_head.py` — Expense head balances and aggregates
- `models/fund_requisition.py` — Requisition workflow and remaining billable logic
- `models/fund_bill.py` — Partial billing and reversal support
- `models/fund_transfer.py` — Transfer workflow and validation
- `models/fund_dashboard.py` — Dashboard aggregates and helpers

Business balances are calculated from ORM records. Workflow actions include server-side validations and permission checks.

## Testing

Run tests inside the Odoo container:

```bash
docker compose exec odoo odoo -d test_db -i nn_fund_management --test-enable --stop-after-init
```

To run tests against an already-installed database:

```bash
docker compose exec odoo odoo -d test_db -u nn_fund_management --test-enable --stop-after-init
```

## Reports

PDF reports provided:

- Fund Allocation
- Requisition
- Transfer
- Fund Summary

## Development & Contributions

Meaningful commit examples:

```
feat: scaffold nn fund management module for odoo 18
feat: add fund accounts and incoming fund posting workflow
feat: implement reusable gm/md approval engine
feat: add allocation, requisition and transfer workflows
feat: add bill posting limits and reversal support
test: cover fund workflows, double spending and security permissions
docs: add docker setup and module architecture guide
```

If you'd like help translating this README to Bengali or adding badges, I can update it.

## Notes

- No raw SQL is used for business logic.
- Views follow Odoo 18 conventions.
- IDs are resolved via XML references and ORM lookups.
