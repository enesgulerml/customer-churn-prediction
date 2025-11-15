# ⚠️ Troubleshooting Guide

This file contains solutions to common environment-specific (non-code) issues that you might encounter while setting up this project.

---

### 1. Docker Build Fails with `cannot allocate memory`

**Symptom:**
When running `docker build ...`, the process fails during the `RUN conda env update` step with one of these errors:
* `Solving environment: \ Killed`
* `ERROR: ... cannot allocate memory`
* `ResourceExhausted: process "/bin/sh -c conda env update..." did not complete`

**Cause:**
This is not a project bug. This is an **environment configuration issue**. The Conda dependency solver (`conda env update`) requires a significant amount of RAM (often >6GB). Your Docker Desktop (running on the WSL 2 backend) has a default memory limit that is too low for this operation.

**Solution:**
You must increase the memory available to the WSL 2 virtual machine by creating (or editing) the `.wslconfig` file in your Windows user profile.

1.  Open **Notepad**
2.  Paste the following content into the blank file. (This example allocates 10GB. Adjust `memory=...` based on your system's total RAM, e.g., `6G` for 8GB total).
    ```ini
    [wsl2]
    memory=10G
    ```
3.  Go to `File -> Save As...`.
4.  In the "Save as type" dropdown, select **"All Files (\*.\*)"**.
5.  In the "File name" box, paste this exact path:
    `C:\Users\[YourUserName]\.wslconfig`
    *(Replace `[YourUserName]` with your actual Windows username, e.g., `enes`)*
6.  Save the file and close Notepad.
7.  **You must fully restart WSL 2 for this change to take effect.** Open a new PowerShell terminal and run:
    ```bash
    wsl --shutdown
    ```
8.  Restart **Docker Desktop** manually.
9.  Once Docker is running (green), return to the project folder and run your `docker build` command again. It should now have enough memory to complete the build.