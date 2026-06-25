# Contributing to Gravit Grover

We love your input! We want to make contributing to Gravit Grover as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `develop`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints (black, flake8)
6. Issue that pull request!

## Development Setup

```bash
# Clone the repository
git clone https://github.com/GravitOpenNetwork/gravit-grover.git
cd gravit-grover

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest tests/

# Run formatting
black core/ tests/

# Run linting
flake8 core/ tests/

# Run type checking
mypy core/
```

## Pull Request Process
* Update the README.md with details of changes if needed
* Update the docs with any new functionality
* The PR will be merged once you have the sign-off of at least one maintainer

## Any contributions you make will be under the Apache 2.0 Software License
When you submit code changes, your submissions are understood to be under the same Apache 2.0 License that covers the project.

## Report bugs using GitHub's issues
We use GitHub issues to track public bugs. Report a bug by opening a new issue.

## Write bug reports with detail, background, and sample code
Great Bug Reports tend to have:

* A quick summary and/or background
* Steps to reproduce
* What you expected would happen
* What actually happens
* Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## License
By contributing, you agree that your contributions will be licensed under its Apache 2.0 License.
