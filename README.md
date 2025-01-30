# SpaceTraders Automation

An automated trading bot for the SpaceTraders game using the official Python API client.

## Setup

1. Install Poetry for dependency management:
```bash
pip install poetry
```

2. Install dependencies:
```bash
poetry install
```

3. Create a `.env` file with your SpaceTraders token:
```
SPACETRADERS_TOKEN=your_token_here
```

## Running Tests

```bash
poetry run pytest
```

## Project Structure

- `game/` - Main game automation code
  - `trader.py` - Core trading bot implementation
- `tests/` - Test suite
  - `test_trader.py` - Tests for trading bot

## Features

- Automated trading system
- System scanning and opportunity detection
- Fleet management
- Market analysis

## Development

This project uses:
- Poetry for dependency management
- pytest for testing
- Type hints for better code quality
- Async/await for efficient API interactions
