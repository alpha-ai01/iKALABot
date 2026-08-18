import importlib
import pkgutil
import os
import sys
import traceback

# Add the current directory to sys.path
sys.path.append(os.getcwd())

# Define packages to check
packages_to_check = [
    'ai',
    'handlers',
    'image',
    'models',
    'plugins',
    'services',
    'utils',
    'voice',
    'main',
    'dispatcher',
    'config'
]

def check_imports():
    for package_name in packages_to_check:
        print(f"Testing import: {package_name}")
        try:
            if package_name in ['main', 'dispatcher', 'config']:
                importlib.import_module(package_name)
            else:
                # Import the package itself
                package = importlib.import_module(package_name)
                # If it's a package, walk through its modules
                if hasattr(package, '__path__'):
                    for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
                        print(f"  Importing: {module_name}")
                        try:
                            importlib.import_module(module_name)
                        except Exception:
                            print(f"    [!] FAILED to import submodule: {module_name}")
                            traceback.print_exc()
                            # We don't exit here, to allow checking other modules
        except Exception:
            print(f"  [!] FAILED to import package: {package_name}")
            traceback.print_exc()
            sys.exit(1)
    print("All package-level imports successful.")

if __name__ == "__main__":
    check_imports()
