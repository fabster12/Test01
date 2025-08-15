# How to Install Pandoc

`pandoc` is a powerful document converter that this application uses to create professional-quality PDF files from Markdown. It is a single command-line tool that needs to be installed on your system.

Below are the recommended installation instructions for your operating system.

---

## Windows

The easiest way to install pandoc is to use the official installer.

1.  Go to the [Pandoc downloads page](https://pandoc.org/installing.html).
2.  Download the latest `.msi` installer for Windows.
3.  Run the installer and follow the on-screen instructions.

Alternatively, if you use the Chocolatey package manager, you can install it by running this command in PowerShell:
```sh
choco install pandoc
```

---

## macOS

The recommended way to install pandoc on macOS is by using the [Homebrew](https://brew.sh/) package manager.

1.  If you don't have Homebrew installed, open your Terminal and install it first.
2.  Once Homebrew is ready, run the following command in your Terminal:
    ```sh
    brew install pandoc
    ```

Alternatively, you can use the official `.pkg` installer from the [Pandoc downloads page](https://pandoc.org/installing.html).

---

## Linux (Debian / Ubuntu)

You can install pandoc using the `apt` package manager.

1.  Open your terminal.
2.  Run the following commands:
    ```sh
    sudo apt-get update
    sudo apt-get install pandoc
    ```

---

## Verifying Installation

Once installed, you can verify that it's working by opening a new terminal or command prompt window and running:

```sh
pandoc --version
```

If the installation was successful, this command will print the installed version of pandoc.
