# AUTHORIZATION MATRIX & RBAC SECURITY ARCHITECTURE

**System Name**: TG KindSync Pro Mission Control  
**Security Classification**: Role-Based Server-Side Enforcement (Zero Frontend-Only Trust)  
**Standard**: NIST SP 800-63B / OWASP Top 10 API Security  

---

## 1. Role Definitions

1. **Super Admin (Root Administrator)**:
   - Reserved strictly for Dr. Amit Singh (`Amit` / `@Kinddoctor4u` / `@Ammitrajput1`).
   - Full unrestricted operational, configuration, user management, and encryption control.
   - Cannot be deleted, disabled, or demoted by any API or user.

2. **Admin (Operational Administrator)**:
   - Full access to operational controls (forwarding routes, engine pause/resume, backups, DLQ purge).
   - Can create/manage `Operator` and `Viewer` accounts. Cannot delete or alter Super Admin.

3. **Operator (Active Engineer)**:
   - Operational streaming access (pause/resume engine, trigger backup snapshots, send Devi AI prompts).
   - Cannot create/delete users or modify forwarding routes.

4. **Viewer (Read-Only Observer)**:
   - Read-only dashboard access (view live telemetry, speeds, dispatched files, and vitals).
   - All state-mutating API requests return `403 Forbidden`.

---

## 2. Server-Side Capability Matrix

| Operational Capability | Super Admin (`super_admin`) | Admin (`admin`) | Operator (`operator`) | Viewer (`viewer`) | Enforcement Layer |
|---|:---:|:---:|:---:|:---:|---|
| **View Dashboard & Telemetry** | ✅ | ✅ | ✅ | ✅ | `/api/status`, `/api/errors` |
| **Search Dispatched Files Ledger** | ✅ | ✅ | ✅ | ✅ | Client & Database SQL |
| **Change Own Password** | ✅ | ✅ | ✅ | ✅ | `/api/auth/change_password` |
| **Pause / Resume Pipeline Engine** | ✅ | ✅ | ✅ | ❌ | `/api/pause` |
| **Reset Display Counters (Standby)** | ✅ | ✅ | ✅ | ❌ | `/api/stats/reset` |
| **Trigger Database Backup Snapshot**| ✅ | ✅ | ✅ | ❌ | `/api/backup` |
| **Interact with Devi AI & Council**  | ✅ | ✅ | ✅ | ❌ | `/api/devi/chat`, `/api/devi/council` |
| **Purge Dead Letter Queue (DLQ)**    | ✅ | ✅ | ❌ | ❌ | `/api/clear_dlq` |
| **Create / Toggle / Delete Routes** | ✅ | ✅ | ❌ | ❌ | `/api/routes/*` |
| **Switch Active Telegram Session**  | ✅ | ✅ | ❌ | ❌ | `/api/telegram/set_active` |
| **Import Telegram Session / OTP**   | ✅ | ✅ | ❌ | ❌ | `/api/telegram/verify_code` |
| **Create New User Accounts**        | ✅ | ✅ | ❌ | ❌ | `/api/auth/create_user` |
| **Delete / Deactivate User Accounts**| ✅ | ⚠️ (Non-Admin only) | ❌ | ❌ | `/api/auth/delete_user` |
| **Delete Root Super Admin**         | ❌ (Immune) | ❌ (Forbidden) | ❌ | ❌ | Protected Server Guard |
