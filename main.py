"""
Assistant - Multi-functional assistant application
Main entry point
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from internal.ui.window import create_app


def main():
    """Application entry point"""
    app = create_app()
    app.run()


if __name__ == "__main__":
    main()

