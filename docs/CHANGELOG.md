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
  - Directory operations: create, delete, rename (with validation)
  - File operations: create, delete, rename, copy, paste
  - Error handling and user feedback for all operations
- Independent chat window (Toplevel)
- Toolbar with icon-based buttons
- Audio batch processing module
  - Audio file scanner with recursive directory scanning
  - Support for multiple audio formats (MP3, FLAC, M4A, AAC, OGG, WMA, WAV, APE, MP4)
  - Audio tag reader (ID3, Vorbis, MP4 tags)
  - Audio tag writer (ID3v2.4 UTF-8 encoding)
  - Encoding detection and conversion (GBK/GB2312 -> UTF-8)
  - Batch metadata processing with multi-threading support
  - Progress display with wget/axel style output
  - Audio processor UI window with options:
    - Fix encoding issues
    - Auto-detect album from directory name
    - Auto-generate title with zero-padding (01, 02, ...)
    - Update tags (write changes to files)
    - Format filename (Number + Album Style, remove ads and decorations)
  - Filename formatting:
    - Unified format: Number + Album Style
    - Automatic removal of ads and decorations (----, URLs, @ symbols, etc.)
    - Smart track number extraction and zero-padding
    - Album style extraction from tags or directory structure
  - Audio processor button (🎵) in toolbar

### Changed
- Main window defaults to file manager
- Chat window is now independent (Toplevel)
- Toolbar button order: File Manager first, Chat second
- Updated README with file management features and correct screenshot paths
- Audio processor button moved from file manager header to main toolbar

### Fixed
- Directory tree subdirectory display with lazy loading
- Directory tree expansion and navigation
- File manager UI layout issues
- Input validation for directory and file names
- Error messages for file operations

### UI Improvements
- Directory tree selection highlighting (blue background, white text)
- Consistent selection style between directory tree and file list
- Custom About dialog with clickable GitHub link
- Single-click selection for directory tree nodes

### Dependencies
- Added `mutagen>=1.47.0` for audio tag processing
- Added `chardet>=5.0.0` for encoding detection

### Planned
- System monitoring features
- Theme customization
- Configuration persistence
- Export/import chat history

