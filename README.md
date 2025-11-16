# Assistant

Multi-functional assistant application with file management and chat capabilities.

## Features

- Chat with AI models via Ollama
  - Streaming response support
  - Model management (download/delete)
  - Chat history
- File management (planned)
- System monitoring (planned)

## Screenshots

### Main Window
![Main Window](screenshots/main.png)

*Main application window with chat interface*

### Model Management
![Model Management](screenshots/model-management.png)

*Model management window for downloading and deleting AI models*

### Chat Interface
![Chat Interface](docs/scrennshot/chat.png)

*Chat interface with streaming AI responses*

> **Note:** Screenshots should be placed in the `screenshots/` directory. Add your own screenshots to showcase the application.

## Requirements

- Python 3.8+
- Ollama service running (for chat feature)

## Installation

```bash
pip install -e .
```

## Usage

### Run from source

```bash
python main.py
```

Or if installed:

```bash
assistant
```

### Run executable

After building (see [Building](docs/BUILD.md)):

```bash
# Windows
dist/assistant.exe

# Linux/Mac
./dist/assistant
```

## Project Structure

```
assistant/
├── main.py                  # Application entry point
├── internal/                # Internal implementation
│   ├── model/              # Data models
│   ├── ui/                 # UI components
│   ├── chat/               # Chat module
│   └── file/               # File management module
├── pkg/                     # Public packages
│   ├── api/                # API clients
│   └── utils/              # Utility functions
└── assets/                 # Static resources
```

## Changelog

See [CHANGELOG.md](docs/CHANGELOG.md) for a list of changes and version history.

## License

MIT

