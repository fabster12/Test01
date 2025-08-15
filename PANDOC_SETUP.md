# Pandoc Installation Guide

Pandoc is a universal document converter that AI Booksmith uses to create professional-quality PDF manuscripts and covers. To use the "Build Package" feature, you need to have Pandoc and a LaTeX distribution installed on your system.

## Installation

### Windows

1.  **Install Chocolatey:** If you don't have it, open PowerShell as Administrator and run:
    ```powershell
    Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    ```
2.  **Install Pandoc and MiKTeX (LaTeX):**
    ```powershell
    choco install pandoc miktex -y
    ```

### macOS

1.  **Install Homebrew:** If you don't have it, open Terminal and run:
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```
2.  **Install Pandoc and MacTeX (LaTeX):**
    ```bash
    brew install pandoc mactex
    ```
    *Note: MacTeX is a large download.*

### Linux (Debian/Ubuntu)

1.  **Install Pandoc and TeX Live:**
    ```bash
    sudo apt-get update
    sudo apt-get install pandoc texlive-latex-base texlive-fonts-recommended texlive-latex-extra -y
    ```

## Verification

After installation, open a new terminal or command prompt and run:

```bash
pandoc --version
```

If the installation was successful, you will see the Pandoc version number and other details. You should now be able to successfully build book packages from within the AI Booksmith application.
