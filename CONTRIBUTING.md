# 🤝 Contributing

We appreciate your interest in contributing to our personal study manager project! Your collaboration is invaluable in making this tool better and more secure for everyone.

## 1. Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. We expect all contributors to demonstrate **mutual respect**, be **inclusive**, and maintain a positive working environment.

## 2. What to Contribute

All help is welcome, whether in code, documentation, or ideas:

* **Reporting Bugs:** Found unexpected behavior? Please open an **Issue** in the appropriate tab.
* **Suggesting Features:** Have an idea that would improve the study experience? Open an **Issue** for discussion.
* **Code Fixes:** Fix existing bugs or implement simple, well-defined features.
* **Documentation:** Improve the `README.md` or the internal code documentation.

**💡 Tip:** For major features or complex changes, **please open an Issue first** to discuss the design and scope before you start coding.

## 3. Local Setup (Getting Started)

To start coding, follow these steps to set up your development environment.

### Prerequisites

Ensure you have **Python (version 3.9+)** and **`pip`** installed.

### 1. Fork and Clone

1.  **Fork** the main repository on GitHub.
2.  Clone your local copy:

    ```bash
    git clone [https://github.com/](https://github.com/)[YOUR_USERNAME]/[PROJECT_NAME].git
    cd [PROJECT_NAME]
    ```

### 2. Configure the Virtual Environment

We highly recommend using a virtual environment (`venv`) to isolate project dependencies:

```bash
# Create and activate the virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate  # Windows Powershell

# Install Flask and other library dependencies
pip install -r requirements.txt
