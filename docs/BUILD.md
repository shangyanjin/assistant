# Building Executable

## Prerequisites

Install PyInstaller:

```bash
pip install pyinstaller
```

## Build Methods

### Method 1: Using build script (Recommended)

**Windows:**
```bash
build.bat
```

**Linux/Mac:**
```bash
chmod +x build.sh
./build.sh
```

### Method 2: Using PyInstaller directly

```bash
pyinstaller build.spec
```

### Method 3: Quick build (one-file)

```bash
pyinstaller --onefile --windowed --name assistant main.py
```

## Output

The executable will be created in the `dist/` directory:
- Windows: `dist/assistant.exe`
- Linux/Mac: `dist/assistant`

## Notes

- The build uses `build.spec` configuration file
- Console window is disabled (GUI only)
- All necessary modules are included as hidden imports
- No external dependencies required (uses only Python standard library)

## Troubleshooting

If the executable doesn't work:
1. Check if all modules are included in `hiddenimports` in `build.spec`
2. Try building with `--debug=all` to see detailed output
3. Check if tkinter is available in your Python installation

