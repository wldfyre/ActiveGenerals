#!/usr/bin/env python3
"""
Example: Including files from other directories in your Python project
"""

import sys
import os
from pathlib import Path

# Method 1: Using sys.path (like main.py does)
def method_1_sys_path():
    """Add project root to Python path"""
    project_root = Path(__file__).parent.parent  # Go up from current file
    sys.path.insert(0, str(project_root))

    # Now you can import from anywhere in the project
    from config.config_manager import ConfigManager
    from models.general import General
    from ui.main_window import MainWindow

# Method 2: Using relative imports with pathlib (like config_manager.py does)
def method_2_pathlib_navigation():
    """Navigate to files using pathlib relative to current file"""

    # From config/config_manager.py, go to project root
    project_root = Path(__file__).parent.parent

    # Access files in other directories
    config_file = project_root / "config.json"
    resources_dir = project_root / "Resources"
    template_file = resources_dir / "EvonyActiveGenerals.xltx"

    # Read files from other directories
    if config_file.exists():
        with open(config_file, 'r') as f:
            print("Config file found!")

    if template_file.exists():
        print("Template file found!")

# Method 3: Using os.path for file operations
def method_3_os_path():
    """Use os.path for file operations across directories"""

    # Get current file's directory
    current_dir = os.path.dirname(__file__)

    # Navigate to project root (up two levels from config/)
    project_root = os.path.dirname(os.path.dirname(current_dir))

    # Build paths to other directories
    config_path = os.path.join(project_root, "config.json")
    resources_path = os.path.join(project_root, "Resources")
    template_path = os.path.join(resources_path, "EvonyActiveGenerals.xltx")

    print(f"Project root: {project_root}")
    print(f"Config path: {config_path}")
    print(f"Template path: {template_path}")

# Method 4: Environment variable approach
def method_4_environment_variable():
    """Use environment variables to define project paths"""

    # Set in your main.py or as environment variable
    project_root = os.environ.get('EVONY_PROJECT_ROOT', Path(__file__).parent.parent)

    # Use throughout the application
    config_dir = Path(project_root) / "config"
    resources_dir = Path(project_root) / "Resources"

    print(f"Config directory: {config_dir}")
    print(f"Resources directory: {resources_dir}")

# Method 5: Configuration-based paths
def method_5_config_based():
    """Store paths in configuration and resolve them"""

    # This is similar to how your config_manager.py works
    class PathResolver:
        def __init__(self):
            self.project_root = Path(__file__).parent.parent

        def get_config_path(self, filename="config.json"):
            return self.project_root / filename

        def get_resource_path(self, filename):
            return self.project_root / "Resources" / filename

        def get_temp_path(self, filename):
            return self.project_root / "Temp" / filename

    resolver = PathResolver()
    config_path = resolver.get_config_path()
    template_path = resolver.get_resource_path("EvonyActiveGenerals.xltx")

    print(f"Resolved config path: {config_path}")
    print(f"Resolved template path: {template_path}")

# Method 6: Using importlib for dynamic imports
def method_6_importlib():
    """Use importlib for dynamic module loading"""

    import importlib.util

    def load_module_from_path(module_name, file_path):
        """Load a Python module from a file path"""
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    # Example: Load a module from another directory
    project_root = Path(__file__).parent.parent
    config_module_path = project_root / "config" / "config_manager.py"

    if config_module_path.exists():
        config_module = load_module_from_path("config_manager", config_module_path)
        ConfigManager = config_module.ConfigManager
        print("Dynamically loaded ConfigManager class")

if __name__ == "__main__":
    print("=== Python File Inclusion Methods ===\n")

    print("1. Method 1 - sys.path approach:")
    method_1_sys_path()
    print()

    print("2. Method 2 - pathlib navigation:")
    method_2_pathlib_navigation()
    print()

    print("3. Method 3 - os.path approach:")
    method_3_os_path()
    print()

    print("4. Method 4 - environment variables:")
    method_4_environment_variable()
    print()

    print("5. Method 5 - configuration-based:")
    method_5_config_based()
    print()

    print("6. Method 6 - importlib dynamic loading:")
    method_6_importlib()
    print()

    print("=== Summary ===")
    print("Your project currently uses:")
    print("- Method 1 (sys.path) in main.py")
    print("- Method 2 (pathlib navigation) in config_manager.py")
    print("- Method 2 (pathlib navigation) in main_window.py")
    print()
    print("Choose the method that best fits your needs!")