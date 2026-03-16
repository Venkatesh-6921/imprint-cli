# 🔏 Imprint v2

**Stamp your developer environment on any machine.**

Imprint is a premium CLI tool inspired by the Gemini CLI experience. It allows you to snapshot your entire machine's developer setup — from dotfiles and VS Code extensions to global packages and shell configurations — and restore it perfectly on a new machine in seconds.

---

## ✨ Features

- **🚀 Instant Snapshot:** Capture EVERYTHING with `imp snapshot`.
- **🔄 Zero-Touch Restore:** Rebuild your world with `imp restore`.
- **💎 Premium UI:** Branded themes, dynamic progress bars, and high-fidelity terminal aesthetics.
- **🛡️ Hardened Safety:** Automated filtering of SSH keys, tokens, and secrets via a non-bypassable `.imprintignore` system.
- **🌐 Cloud Sync:** Built-in GitHub integration for secure, versioned backups.
- **🍎 Universal:** First-class support for Windows, macOS, Linux, and WSL.

---

## 🚀 Quick Start

### 1. Installation
```bash
pip install imprint-cli
```

### 2. Capture Your World
```bash
imp snapshot
```
*On first run, Imprint will prompt you for an optional GitHub repository URL to enable cloud syncing.*

### 3. Move to a New Machine
```bash
imp restore https://github.com/your-username/my-imprint-config.git
```

---

## 🛠️ Usage

| Command | Action |
|---|---|
| `imp snapshot` | Captures your current environment and pushes to GitHub. |
| `imp restore` | Restores environment from local or GitHub source. |
| `imp diff` | See exactly what has changed since your last snapshot. |
| `imp update` | Quick alias for `snapshot + push`. |
| `imp status` | View a high-level overview of your tracked configuration. |

---

## 🔍 What gets captured?

- **Dotfiles:** `.zshrc`, `.bashrc`, `.gitconfig`, `.vimrc`, and more.
- **VS Code:** Complete extension manifest + `settings.json`.
- **Packages:** Global packages from `pip`, `npm`, `apt`, `brew`, and `winget`.
- **Shell:** Frameworks (Oh My Zsh), themes, and plugin configurations.
- **Scripts:** Everything in your `~/bin` folder.
- **System:** Runtimes like Python, Node.js, and Git versions.

---

## 🔏 Security First

Imprint is designed to be secure by default. It **never** captures sensitive files. Our `.imprintignore` system automatically blocks:
- 🔑 SSH Keys (`.ssh/id_*`)
- 🎫 Tokens & Secrets (`*.token`, `*secret*`)
- 🌐 Environment files (`.env`)
- ☁️ Cloud credentials (`.aws/`, `.kube/`)
- 📜 Shell history (`.zsh_history`)

---

## 📦 For Developers: Publishing to PyPI

### Pre-requisites
- A [PyPI](https://pypi.org/) account.
- An API Token (`__token__`).

### Build & Upload
1. **Build the package:**
   ```bash
   python -m build
   ```
2. **Upload securely:**
   ```powershell
   # Set credentials in environment variables
   $env:TWINE_USERNAME="__token__"
   $env:TWINE_PASSWORD="pypi-your-token-here"
   python -m twine upload dist/*
   ```

> [!TIP]
> **Forgot your PyPI Token?**
> PyPI API tokens are only shown once. If you lose or forget it:
> 1. Log in to your PyPI account.
> 2. Go to **Account Settings**.
> 3. Scroll to **API tokens**.
> 4. Delete the lost token and click **Add API token**.
> 5. Copy the new token immediately!

---

## 📄 License

MIT © [Venkatesh](https://github.com/Venkatesh-6921)
