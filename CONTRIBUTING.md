# Contributing to stock-agent

Thanks for your interest in contributing.

## Ways to contribute

- Report reproducible bugs and documentation issues.
- Improve tests, documentation, data-source adapters, strategy plugins, and broker adapters.
- Propose focused features through an issue before making large architectural changes.

## Development setup

Use Python 3.11 or 3.12.

```bash
python -m venv .venv
# activate the environment for your platform
pip install -e ./shared
pip install -e "./backend[dev]"
pip install -e "./trade-executor[dev]"
```

Run checks before opening a pull request:

```bash
ruff check .
cd backend && pytest
cd ../trade-executor && pytest
```

## Pull requests

Keep changes focused, explain the motivation and behavior change, and add or update tests when practical. Do not commit credentials, account information, API keys, local configuration, databases, or brokerage screenshots containing personal information.

## Financial safety

Paper/Demo mode should be used for development and testing. Changes affecting live-client automation should preserve dry-run safeguards and document any behavior that could submit or alter an order.

## License

By contributing, you agree that your contributions will be licensed under the repository's MIT License.
