# Contributing to Gabriel

Thank you for your interest in contributing to Gabriel! To keep the project stable and focused, please follow these guidelines.

Before diving into the code, please read the [Architecture Guide](docs/ARCHITECTURE.md) and the [API Reference](docs/API_REFERENCE.md) to understand how Gabriel works under the hood.

## Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/gabriel.git
   cd gabriel
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python src/main.py
   ```

## Testing

We require tests to pass before any PR can be merged. 

To run the unit tests:
```bash
python -m unittest discover tests -v
```

Ensure that your new code is covered by tests and does not break existing functionality (especially authentication and SQLite concurrency).

## Pull Request Process
1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. Update the README.md with details of changes to the interface or architecture.
4. Ensure the test suite passes locally.
5. Open a Pull Request with a clear description of the problem and your solution.
