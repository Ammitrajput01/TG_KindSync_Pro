# 🛡️ Security Policy & Vulnerability Disclosure

## 📌 Overview
The **TG KindSync Pro & Kind Doctor Bot** project places the highest priority on user privacy, cryptographic integrity, and secure communication. As an enterprise-grade medical and Telegram cloud management suite handling high-throughput MTProto streaming and multi-tenant user sessions, security is built into every layer of our architecture.

---

## 🔒 Supported Versions

We actively provide security patches, updates, and threat mitigations for the following versions:

| Version | Status | Security Support |
| :--- | :--- | :--- |
| **v16.0.x (Current Enterprise)** | 🟢 Active | Full Continuous Security Updates |
| **v15.x.x** | 🟡 Maintenance | Critical CVE & Session Fixes Only |
| **< v15.0.0** | 🔴 End of Life | Not Supported; Please Upgrade |

---

## 🛡️ Core Security Architecture & Guarantees

1. **Multi-Tenant Session Isolation & Fernet AES-256 Encryption**:
   - All user session strings connected via `/connect` are encrypted at rest using **Fernet 256-bit symmetric encryption** (`devi/operator/session_vault.py`).
   - Sessions are strictly partitioned by numeric `user_id`. One user can **never** access or trigger operations using another user's session.
2. **Zero Plaintext Logging**:
   - Phone numbers, login verification codes (OTP), passwords, and session strings are **strictly excluded** from all loggers, journals, and telemetry streams.
3. **Cryptographic Telegram WebApp Authentication**:
   - All Telegram Mini App (TMA) endpoints require cryptographic **HMAC-SHA256 signature verification** against the bot's secret key (`devi/operator/tma/tma_auth.py`). Tampered, replayed, or forged queries are rejected with HTTP 403 Forbidden.
4. **Strict Master Admin Boundaries**:
   - Master administration commands, server reboots, and sensitive diagnostic views are strictly locked to Dr. Amit Singh's verified accounts:
     - `@Kinddoctor4u` (User ID: `1553619403`)
     - `@Ammitrajput1` (User ID: `759038032`)

---

## 🚨 Reporting a Vulnerability

If you discover a security vulnerability, flaw, or potential exploit in this repository, **please do not disclose it publicly** through public GitHub issues or public channels.

Instead, please report it directly and confidentially to the Project Architect:

* **Primary Security Telegram**: [@Kinddoctor4u](https://t.me/Kinddoctor4u)
* **Secondary Telegram**: [@Ammitrajput1](https://t.me/Ammitrajput1)
* **Confidential Security Email**: `Ammitrajput1@gmail.com`

### 📋 What to Include in Your Report:
1. **Description of the vulnerability**: A clear summary of the issue.
2. **Steps to reproduce**: Minimal proof-of-concept (PoC) code or step-by-step instructions.
3. **Potential impact**: How an attacker could exploit the issue and what data/systems might be affected.
4. **Any suggested mitigations**: If you have a proposed fix or remediation.

---

## ⏱️ Response & Disclosure Timeline

* **Initial Acknowledgment**: Within **24 hours** of receipt.
* **Triage & Assessment**: Within **48 hours** with severity classification.
* **Remediation & Patch**: Critical security issues will receive hotfix patches within **3 to 7 days**.
* **Public Advisory**: Published in GitHub Security Advisories only after the fix has been verified and deployed across all production environments.

Thank you for helping keep TG KindSync Pro, Kind Doctor Bot, and our medical community secure! 🩺
