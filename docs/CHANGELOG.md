# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-11-16

### Added
- Initial project structure with Go-style directory organization
- Chat module with Ollama integration
  - Chat UI with message bubbles
  - Streaming response support
  - Chat history management
- Model management
  - Model download functionality
  - Model deletion functionality
  - Model list display
  - Download progress logging
- Settings button (⚙️) in header
- Menu bar with File, Edit, and Help menus
- Host configuration support
- System compatibility checking
- Progress bar for AI generation
- Stop generation functionality

### Technical
- Modular architecture following Go-style project structure
- Separation of concerns: Model, Service, Handler, UI
- API client abstraction for Ollama
- Resource path utilities for packaged execution
- Error handling and user feedback

### Project Structure
```
assistant/
├── main.py                  # Application entry point
├── internal/                # Internal implementation
│   ├── model/              # Data models
│   ├── ui/                 # UI components
│   ├── chat/               # Chat module
│   └── file/               # File management (planned)
├── pkg/                     # Public packages
│   ├── api/                # API clients
│   └── utils/              # Utility functions
└── assets/                  # Static resources
```

## [0.1.1] - 2024-11-17

### Added
- PyInstaller build configuration (`build.spec`)
- Build scripts for Windows (`build.bat`) and Linux/Mac (`build.sh`)
- Build documentation (`docs/BUILD.md`)
- Executable packaging support

### Changed
- Updated README with build instructions
- Updated `.gitignore` to allow `build.spec` in repository

## [Unreleased]

### Added
- File management module with left-right layout
  - Directory tree on the left (lazy loading)
  - File list on the right with details (Name, Date Modified, Type, Size)
  - Resizable paned window
  - Navigation buttons (back, forward, refresh)
  - Search functionality
  - Context menu for file operations
- Independent chat window (Toplevel)
- Toolbar with icon-based buttons

### Changed
- Main window defaults to file manager
- Chat window is now independent (Toplevel)
- Toolbar button order: File Manager first, Chat second

### Fixed
- Directory tree subdirectory display with lazy loading
- Directory tree expansion and navigation
- File manager UI layout issues

### Planned
- System monitoring features
- Theme customization
- Configuration persistence
- Export/import chat history

