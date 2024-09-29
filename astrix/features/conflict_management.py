import toml
import ast
import subprocess
import sys
import os
import shutil

def parse_pyprojecttoml(path):
    """Parse pyproject.toml and return dependencies."""
    with open(path, 'r') as file:
        pyproject = toml.load(file)
    return pyproject.get('tool', {}).get('poetry', {}).get('dependencies', {})

def installTxt(path):
    """Parse requirements.txt and return dependencies."""
    deps = {}
    with open(path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '==' in line:
                pkg, version = line.split('==')
                deps[pkg.strip()] = version.strip()
    return deps

def installSetup(path):
    """Parse setup.py and return dependencies."""
    with open(path, 'r') as file:
        content = file.read()
    tree = ast.parse(content)
    deps = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'setup':
            for keyword in node.keywords:
                if keyword.arg == 'install_requires':
                    deps_list = ast.literal_eval(keyword.value)
                    for dep in deps_list:
                        pkg, version = dep.strip().split('==')
                        deps[pkg] = version
    return deps



def create_venv(env_name, deps):
    """Create a new virtual environment with the given name."""
    if not os.path.exists(env_name):
        subprocess.check_call([sys.executable, "-m", "venv", env_name])
        print(f"Virtual environment '{env_name}' created successfully.")
    else:
        print(f"Virtual environment '{env_name}' already exists.")


    if deps:
        python_executable = os.path.join(env_name, "Scripts", "python") if os.name == 'nt' else os.path.join(env_name, "bin", "python")
    
    # Install each dependency using pip
        print(f"Installing dependencies: {deps} into {env_name}...")
        for dep in deps:
            try:
                subprocess.check_call([python_executable, "-m", "pip", "install", dep])
                print(f"Installed {dep}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {dep}: {str(e)}")
                
        print(f"All dependencies installed in {env_name}.")

    else:
        print("No requirement.txt or setup.py file found")


def delete_venv(env_name):
    """Delete the virtual environment directory."""
    if os.path.exists(env_name):
        shutil.rmtree(env_name)
        print(f"Virtual environment '{env_name}' has been deleted.")
    else:
        print(f"Virtual environment '{env_name}' does not exist.")

def list_venvs():
    """List all recorded virtual environments."""
    if not os.path.exists('venv_record.txt'):
        print("No virtual environments have been recorded.")
        return
    
    with open('venv_record.txt', 'r') as f:
        venvs = f.readlines()
    
    if venvs:
        print("Recorded virtual environments:")
        for venv in venvs:
            print(f"- {venv.strip()}")
    else:
        print("No virtual environments found.")