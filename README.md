# SpaceTraders Automation

An automated trading bot for the SpaceTraders game using the official Python API client. This bot automates various game operations including ship management, trading, mining, and contract fulfillment.

## Features

- 🚀 Automated ship management and navigation
- ⛏️ Mining operations with engineered asteroid detection
- 📈 Contract management and fulfillment
- 🛸 Ship purchasing and fleet expansion
- 🔄 Automated refueling and maintenance
- 💼 Market trading operations

## Requirements

- Python 3.9+
- Poetry (dependency management)
- SpaceTraders API token

## Setup

1. Install Poetry for dependency management:
```bash
pip install poetry
```

2. Install dependencies:
```bash
poetry install
```

3. Run the game:
```bash
poetry run python main.py
```

The script will automatically register a new agent if no token exists, or use your existing token from `token.json` if you have one:
```json
{
    "token": "your_token_here"
}
```

## Running Tests

Run the test suite to verify everything is working:
```bash
poetry run pytest
```

## Project Structure

- `game/` - Main game automation code
  - `trader.py` - Core trading bot implementation with ship and fleet management
  - `register.py` - Agent registration and token management
- `tests/` - Test suite
  - `factories.py` - Test factories for creating game objects
  - `test_trader.py` - Trading bot tests
  - `test_register.py` - Registration tests
- `space-traders-api-client/` - Official SpaceTraders API client

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

This project is open source and available under the MIT License.
