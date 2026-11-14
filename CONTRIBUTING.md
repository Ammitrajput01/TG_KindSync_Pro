# 🤝 Contributing to TG KindSync Pro & Kind Doctor Bot

Welcome! We are thrilled that you want to contribute to **TG KindSync Pro & Kind Doctor Bot**. Whether you are a software engineer, medical student, clinical researcher, or DevOps enthusiast, your contributions help make this high-performance platform even better.

---

## 🧭 Code of Conduct

All contributors and participants are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please treat all community members with kindness, dignity, and professional respect.

---

## 🛠️ How You Can Contribute

1. **Reporting Bugs**: Check the [Issues tab](https://github.com/Ammitrajput01/TG_KindSync_Pro/issues) to see if the bug has already been reported. If not, open a new issue using our **Bug Report** template.
2. **Suggesting Enhancements**: Have an idea for a clinical formula, a faster streaming pacer, or a new TMA mini-app panel? Submit a **Feature Request**.
3. **Writing Code / Pull Requests**:
   - Fix bugs, improve documentation, or optimize algorithms.
   - Expand Clinical Decision Support System (CDSS) formulas in `devi/operator/handlers/clinical.py`.
   - Improve Android Termux cross-compilation support in `requirements-termux.txt` and `KINDSYNC_MASTER.sh`.

---

## 🚀 Development Workflow

### 1. Setting Up Your Local Environment
```bash
# 1. Clone the repository
git clone https://github.com/Ammitrajput01/TG_KindSync_Pro.git
cd TG_KindSync_Pro

# 2. Create and activate a Python virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS/Termux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### 2. Architecture Guidelines & Code Standards
* **O(1) Command Dispatcher**: When adding new bot commands, register them in their appropriate domain folder under `devi/operator/handlers/` using the `$O(1)` `CommandRouter` rather than monolithic `if-elif` checks.
* **Strict Privacy & Isolation**: Never log user tokens, phone numbers, or OTP codes. Ensure all session storage utilizes the Fernet-encrypted vault.
* **Backward Compatibility**: Any changes to core engines (`tg_kindsync_pro.py`, `devi/operator/telegram_bot.py`) must maintain 100% backward compatibility with existing unit tests and dashboard APIs.

### 3. Running Verification Tests
Before submitting any Pull Request, you **must verify that all 17 test suites pass completely**:
```bash
python tests/run_all_tests.py
```
Expected output:
```text
========================================================
   SUMMARY: 17 PASSED | 0 FAILED (Total: 17)
   STATUS: ALL SYSTEM COMPONENTS ARE 100% HEALTHY!
========================================================
```

---

## 📝 Submitting a Pull Request (PR)

1. **Create a Topic Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Commit Your Changes**:
   Follow conventional commit style:
   - `feat(clinical): add pediatric drug dosing formula`
   - `fix(cloner): resolve edge case in topic range selection`
   - `docs(readme): clarify Termux installation steps`
3. **Push to Your Fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
4. **Open a PR**: Fill out the Pull Request template completely, linking any relevant issues.

---

## 💬 Questions & Support

Need guidance or want to discuss an architectural feature?
* **Project Maintainer**: Dr. Amit Singh (Kind Doctor)
* **Telegram**: [@Kinddoctor4u](https://t.me/Kinddoctor4u) · [@Ammitrajput1](https://t.me/Ammitrajput1)
* **Email**: `Ammitrajput1@gmail.com`
