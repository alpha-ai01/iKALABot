import os
import ast

def is_internal_module(module_name, project_root):
    # Check if the module exists as a file or directory within project_root
    module_path = module_name.replace(".", "/")
    return os.path.exists(os.path.join(project_root, module_path + ".py")) or \
           os.path.exists(os.path.join(project_root, module_path))

def verify_imports(directory):
    errors = 0
    # List of known project-level packages/folders to ignore
    # (these are already handled by the internal check)
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    try:
                        tree = ast.parse(f.read())
                    except SyntaxError:
                        continue
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom):
                            if node.module:
                                # Check if it looks like an internal import
                                # This is a heuristic: check if the top-level module is internal
                                top_level_module = node.module.split(".")[0]
                                if is_internal_module(top_level_module, directory):
                                    if not is_internal_module(node.module, directory):
                                        print(f"Potential internal import error in {file_path}: 'from {node.module} import ...'")
                                        errors += 1
    return errors

if __name__ == "__main__":
    project_root = os.getcwd()
    print("Verifying project structure and internal imports...")
    errors = verify_imports(project_root)
    if errors == 0:
        print("✓ All internal imports look correct.")
    else:
        print(f"✗ Found {errors} potential import errors.")
        exit(1)
