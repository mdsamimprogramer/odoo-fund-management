# NN Fund Management

Production-quality Odoo 18 Community Edition module for the NN Services & Engineering Ltd. Trainee Software Developer assessment.

## Features

- Bank and cash fund accounts with received, available, held and assigned balances.
- Incoming fund posting with duplicate transaction reference prevention per account.
- Fund allocation workflow: Draft, GM Approval, MD Approval, Approved, Rejected and Cancelled.
- Reusable approval engine for allocations, requisitions and transfers.
- Configurable GM and MD approvers with no self approval.
- Projects and expense heads with computed allocated, available, hold, spent and transfer balances.
- Requisitions with hold, reserve, billable remaining amount and closure.
- Custom bills with partial billing, over-billing prevention and reversal.
- Fund transfers between projects and expense heads.
- Chatter, activities and approval/audit history.
- Dashboard and PDF reports.
- Automated workflow, balance, bill limit and security tests.

## Docker Setup

From the project root:

```bash
docker compose up -d
```

Open Odoo at:

```text
http://localhost:8069
```

The compose stack uses:

- Odoo 18
- PostgreSQL 16
- `./custom_addons` mounted at `/mnt/extra-addons`

## Installation

1. Start the Docker stack.
2. Create or open an Odoo database.
3. Enable developer mode.
4. Update Apps List.
5. Search for `NN Fund Management`.
6. Install the module.

## Configuration

Go to Fund Management > Configuration > Approval Configuration.

Configure approvers for:

- Allocation Approval
- Requisition Approval
- Transfer Approval

Assign users to these security groups as needed:

- Fund User
- Finance User
- GM Approver
- MD Approver
- Fund Administrator

## Usage

1. Create Fund Accounts.
2. Post Incoming Funds as a Finance User.
3. Create Projects and Expense Heads.
4. Submit Fund Allocations.
5. Approve first as GM, then as MD.
6. Create Requisitions against approved project or expense head balances.
7. Post partial Bills against approved requisitions.
8. Transfer approved balances between projects and expense heads when required.
9. Monitor balances from the Dashboard.

## Architecture

The module is split by business responsibility:

- `models/fund_account.py`: source fund accounts and computed account balances.
- `models/incoming_fund.py`: incoming receipts and transaction reference uniqueness.
- `models/approval_mixin.py`: reusable approval and activity engine.
- `models/approval.py`: approval configuration and audit history.
- `models/fund_allocation.py`: allocation workflow and source balance reservation.
- `models/fund_project.py`: computed project balances.
- `models/expense_head.py`: computed expense head balances.
- `models/fund_requisition.py`: requisition workflow and remaining billable logic.
- `models/fund_bill.py`: partial bill posting and reversal.
- `models/fund_transfer.py`: transfer workflow and over-transfer prevention.
- `models/fund_dashboard.py`: dashboard aggregates.

Balances are computed from business records with ORM dependencies. Workflow actions enforce server-side permissions and validations.

## Testing

Run tests from inside the Odoo container:

```bash
docker compose exec odoo odoo -d test_db -i nn_fund_management --test-enable --stop-after-init
```

For an already installed database:

```bash
docker compose exec odoo odoo -d test_db -u nn_fund_management --test-enable --stop-after-init
```

## Reports

Available PDF reports:

- Fund Allocation
- Requisition
- Transfer
- Fund Summary

## Meaningful Commit History Examples

```text
feat: scaffold nn fund management module for odoo 18
feat: add fund accounts and incoming fund posting workflow
feat: implement reusable gm/md approval engine
feat: add allocation, requisition and transfer workflows
feat: add bill posting limits and reversal support
feat: add dashboard, reports and audit history
test: cover fund workflows, double spending and security permissions
docs: add docker setup and module architecture guide
```

## Notes

- No raw SQL is used for business logic.
- Views use Odoo 18 `list` views.
- Deprecated `attrs` and `states` XML syntax is not used.
- IDs are resolved via XML references and ORM lookups.
