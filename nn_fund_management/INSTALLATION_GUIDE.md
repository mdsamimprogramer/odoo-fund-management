# NN Fund Management Module - Installation & Deployment Guide

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Deployment](#deployment)
4. [Troubleshooting](#troubleshooting)
5. [Production Checklist](#production-checklist)

---

## Installation

### Prerequisites

- Odoo 18.0 installed and running
- PostgreSQL database
- Sufficient file system permissions in Odoo addons directory
- Python 3.9 or higher

### Step 1: Copy Module Files

```bash
# Navigate to your Odoo addons directory
cd /path/to/odoo/addons/

# Copy the nn_fund_management module
cp -r /path/to/nn_fund_management .

# Verify module structure
ls -la nn_fund_management/
```

### Step 2: Update Module List in Odoo

1. Log in to Odoo as Administrator
2. Navigate to: **Apps → Update Apps List**
3. Click "Update" button
4. Wait for update to complete

### Step 3: Install the Module

1. Go to: **Apps → Apps** (or search directly)
2. Search for: "Fund Management" or "nn_fund_management"
3. Click on the module card
4. Click **Install** button
5. Confirm installation

### Step 4: Verify Installation

1. Navigate to: **Fund Management → Fund Requests**
2. You should see an empty list or demo records
3. Check that menu items appear correctly
4. Verify user groups are created

---

## Configuration

### User Groups Setup

#### 1. Create Fund Users Group

1. Go to: **Settings → Manage Users**
2. For each Fund User:
   - Edit user profile
   - Go to **Access Rights** tab
   - Find "NN Fund Management" section
   - Check: **Fund User**
   - Save

#### 2. Create Fund Managers Group

1. Go to: **Settings → Manage Users**
2. For each Fund Manager:
   - Edit user profile
   - Go to **Access Rights** tab
   - Find "NN Fund Management" section
   - Check: **Fund Manager**
   - Save

### Sequence Configuration (Optional)

To customize the request number format:

1. Go to: **Settings → Sequences & Identifiers**
2. Search for: "Fund Request Sequence"
3. Edit the sequence:
   - Change **Prefix** format as needed
   - Adjust **Padding** (number of digits)
   - Modify **Next Number** if needed

**Examples:**

- `FR/%(year)s/%(seq)s` → FR/2024/00001
- `FUND-%(seq)s` → FUND-00001
- `%(company_code)s/%(year)s/%(month)s/%(seq)s` → ABC/2024/06/00001

### Email Notifications (Optional)

To set up email notifications for approval:

1. Go to: **Settings → Technical → Email → Email Templates**
2. Create new template for fund request approval
3. Link in workflow methods if needed

---

## Deployment

### Development to Staging

```bash
# Backup database
pg_dump odoo_db > backup_before_deploy.sql

# Copy module to staging
cp -r nn_fund_management /staging/addons/

# Install/update in staging Odoo
# (Follow installation steps above)

# Test thoroughly in staging environment
```

### Staging to Production

```bash
# Backup production database
pg_dump production_db > backup_before_prod.sql

# Create maintenance window notification
# (Notify users of downtime)

# Shutdown Odoo
sudo systemctl stop odoo

# Backup current addons
cp -r /production/addons /production/addons.backup

# Deploy module
cp -r nn_fund_management /production/addons/

# Restart Odoo
sudo systemctl start odoo

# Verify installation
# (Navigate to Fund Management menu)

# Notify users of deployment completion
```

### Docker Deployment

```yaml
# In docker-compose.yml, ensure volume mapping:
services:
  odoo:
    volumes:
      - ./addons:/mnt/extra-addons

# Copy module
docker cp nn_fund_management odoo_container:/mnt/extra-addons/

# Restart container
docker-compose restart odoo

# Install module via web interface
```

---

## Troubleshooting

### Issue: Module not appearing in Apps list

**Solution:**

1. Check file permissions: `ls -la nn_fund_management/`
2. Verify manifest syntax: `python -m py_compile __manifest__.py`
3. Check Odoo logs: `tail -f /var/log/odoo/odoo.log`
4. Restart Odoo service
5. Clear browser cache

### Issue: "AccessError" when accessing Fund Requests

**Solution:**

1. Verify user group assignment
2. Check group permissions in security/ir_model_access.csv
3. Ensure user is in appropriate group
4. Clear browser cache and session

### Issue: Report not generating

**Solution:**

1. Verify report files are loaded:
   - Check `ir.actions.report` table
   - Verify template reference is correct
2. Check XML syntax for report template
3. Ensure all required fields exist in model
4. Check Odoo logs for template errors

### Issue: Workflow buttons not appearing

**Solution:**

1. Verify user permissions
2. Check button state conditions in view
3. Ensure status field has correct value
4. Verify groups attribute in button
5. Clear browser cache

### Issue: Sequence not auto-generating

**Solution:**

1. Verify sequence exists:
   - Go to Settings → Sequences
   - Search for "Fund Request"
2. Check sequence code: `fund.request`
3. Verify data file in manifest
4. Check field default value:
   ```python
   default=lambda self: self.env['ir.sequence'].next_by_code('fund.request')
   ```

### Issue: Database constraints not enforced

**Solution:**

1. Clear module cache:
   ```bash
   rm -rf ~/.local/share/Odoo/
   ```
2. Reinstall module
3. Run module tests
4. Check constraint in model

### Issue: Demo data not loading

**Solution:**

1. Ensure demo data file is listed in manifest
2. Check XML syntax: `python -m xml.etree.ElementTree data/fund_request_demo.xml`
3. Verify datetime imports in demo XML
4. Reinstall module with demo data

---

## Production Checklist

### Before Going Live

- [ ] All tests pass in staging environment
- [ ] Database backup created
- [ ] Backup rollback plan documented
- [ ] User groups configured correctly
- [ ] Security permissions verified
- [ ] Sequence format customized (if needed)
- [ ] Email templates configured (if using)
- [ ] User documentation prepared
- [ ] Training completed for users
- [ ] Monitoring/alerts configured

### Day 1 - After Deployment

- [ ] Monitor Odoo logs for errors
- [ ] Test all workflows with sample data
- [ ] Verify group permissions work
- [ ] Test PDF report generation
- [ ] Monitor system performance
- [ ] Check for any access denied errors
- [ ] Gather user feedback
- [ ] Have rollback plan ready

### Week 1 - After Deployment

- [ ] Review usage patterns
- [ ] Check for any bugs or issues
- [ ] Verify data integrity
- [ ] Monitor server performance
- [ ] Collect user feedback
- [ ] Document any customizations
- [ ] Plan enhancements (if needed)

### Ongoing Maintenance

- [ ] Regular database backups
- [ ] Monitor module for updates
- [ ] Review access logs periodically
- [ ] Archive old fund requests (if needed)
- [ ] Update user documentation as needed
- [ ] Performance optimization (if needed)

---

## Quick Reference

### Important Files

| File                                       | Purpose              |
| ------------------------------------------ | -------------------- |
| `__manifest__.py`                          | Module configuration |
| `models/fund_request.py`                   | Core model and logic |
| `views/fund_request_views.xml`             | UI views             |
| `security/ir_model_access.csv`             | Access rights        |
| `data/fund_request_sequence.xml`           | Auto-numbering       |
| `reports/fund_request_report_template.xml` | PDF template         |

### Key Paths

| Item     | Path                                       |
| -------- | ------------------------------------------ |
| Module   | `/path/to/odoo/addons/nn_fund_management/` |
| Logs     | `/var/log/odoo/odoo.log`                   |
| Config   | `/etc/odoo/odoo.conf`                      |
| Database | PostgreSQL database                        |
| Backups  | `/backups/`                                |

### Database Tables

| Table             | Description          |
| ----------------- | -------------------- |
| `fund_request`    | Fund request records |
| `res_groups`      | User groups          |
| `ir_model_access` | Access rights        |
| `ir_sequence`     | Sequences            |

---

## Support & Resources

- **Odoo Documentation**: https://www.odoo.com/documentation/18.0/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Python Docs**: https://docs.python.org/3.9/
- **Development Team**: [Contact info]

---

**Last Updated:** 2024-06-20  
**Module Version:** 18.0.1.0.0  
**License:** LGPL-3
