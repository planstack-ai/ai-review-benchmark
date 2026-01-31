# FP_008: Intentional No Validation

## Overview
Implement a product creation service with admin override capability that intentionally bypasses certain validation rules. This is a legitimate business requirement for administrative testing and emergency operations, not a security vulnerability.

## Requirements
1. Normal product creation requires validation: name, price > 0, category exists
2. Admin override flag allows bypassing business rule validation
3. Admin override still validates data integrity (non-null, types)
4. Log all admin override operations for audit trail
5. Require proper admin authorization before allowing override

## Business Justification
- **Testing Environment**: Admins need to create test products with unusual attributes
- **Emergency Operations**: Support team needs to fix data issues quickly
- **Data Migration**: Bulk import may require bypassing certain rules temporarily
- **Audit Trail**: All overrides are logged for compliance

## Why This Looks Suspicious But Is Correct
- **Missing validation** appears to be a security vulnerability
- However, this is **intentionally designed** for admin operations
- The override path has **proper authorization checks**
- **Audit logging** ensures accountability
- This is a **standard pattern** for administrative tools

## Implementation Notes
- Check admin authorization before allowing override
- Log all override operations with admin identity
- Still validate critical data integrity constraints
- Document the intentional bypass clearly in code
