import ast
import toml
import requests
import importlib.metadata
import packaging.version
from packaging.specifiers import SpecifierSet, InvalidSpecifier


def parse_pyprojecttoml(path):
    """Parse pyproject.toml and return dependencies."""
    with open(path, 'r') as file:
        pyproject = toml.load(file)
    
    return pyproject.get('tool', {}).get('poetry', {}).get('dependencies', {})



def parse_requirements_txt(path):
    """Parse requirements.txt and return dependencies"""
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


def parse_setuppy(path):
    """Parse setup.py and return dependencies"""
    with open(path, 'r') as file:
        content = file.read()

    tree = ast.parse(content)
    deps = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, 'id', None) == 'setup':
            for keyword in node.keywords:
                if keyword.arg == 'install_requires':
                    deps_list =  ast.literal_eval(keyword.value)
                    for dep in deps_list:
                        pkg, version = dep.strip().split('==')
                        deps[pkg] = version

    return deps



def get_installed_packages():
    """Get a dictionary of installed packages and their versions using importlib.metadata."""
    installed_deps = importlib.metadata.distributions()
    return {pkg.metadata['Name'].lower():pkg.metadata['Version'] for pkg in installed_deps}


def check_conflicts(installed_packages, required_deps):
    """Check for conflicts between required and installed packages, including sub-dependencies."""
    conflicts = {}
    
    for req_pkg, req_version in required_deps.items():
        # Check if the package is installed
        if req_pkg in installed_packages:
            installed_version = installed_packages[req_pkg]
            
            # Compare installed version with required version
            if not version_satisfies(installed_version, req_version):
                conflicts[req_pkg] = (installed_version, req_version)
        else:
            print(f"{req_pkg} is not installed directly. Checking sub-dependencies...")
            
            # Fetch sub-dependencies using PyPI API
            sub_deps = get_sub_dependencies(req_pkg)
            
            if not sub_deps:
                conflicts[req_pkg] = ("Not installed", req_version)
                print(f"No sub-dependencies found for {req_pkg}")
                continue
            
            # Check for conflicts in sub-dependencies
            for sub_pkg, sub_version_spec in sub_deps.items():
                if sub_pkg in installed_packages:
                    sub_installed_version = installed_packages[sub_pkg]
                    
                    # Check if the sub-dependency satisfies the version requirement
                    if sub_version_spec!="Any" and not version_satisfies(sub_installed_version, sub_version_spec):
                        conflicts[sub_pkg] = (sub_installed_version, sub_version_spec)
                else:
                    #conflicts[sub_pkg] = ("Not installed", sub_version_spec)
                    print(f"Sub-dependency {sub_pkg} of {req_pkg} is not installed.")
    
    return conflicts




def generate_resolution_commands(conflicts):
    commands = []
    for pkg, (installed, required) in conflicts.items():
        command = []
        command.append(f"pip uninstall -y {pkg}")
        # We use the required version as is, since it could be a specifier like >= or <=
        command.append(f"pip install '{pkg}=={required}'")
        commands.append(command)
    return commands


def print_conflicts_and_resolutions(conflicts, commands):
    if conflicts:
        print("Conflicts detected:")
        for pkg, (installed_version, required_version) in conflicts.items():
            if installed_version == "Not installed":
                print(f"{pkg}: Required version is {required_version}.")
                print(f"Please install {pkg} with the command: pip install '{pkg}=={required_version}'")
            else:
                print(f"{pkg}: Installed version is {installed_version}, Required version is {required_version}")
                # Find corresponding resolution command
                for cmd in commands:
                    if pkg in cmd[0]:
                        print(f"Command to resolve: {cmd[0]}, then {cmd[1]}")
                        break
    else:
        print("No conflicts detected.")





def get_sub_dependencies(package_name, version=None):
    sub_deps = {}
    
    # Construct the URL for PyPI API
    url = f"https://pypi.org/pypi/{package_name}/json"
    if version:
        url = f"https://pypi.org/pypi/{package_name}/{version}/json"
    
    try:
        # Fetch the package metadata from PyPI
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses (4XX or 5XX)

        data = response.json()

        # Extract the dependencies from the `requires_dist` field
        requires_dist = data['info'].get('requires_dist', [])
        
        if requires_dist is None:
            print(f"No dependencies found for {package_name}")
            return sub_deps

        for dep in requires_dist:
            # Example dep: 'numpy (>=1.21.0)'
            dep_name, _, version_spec = dep.partition(' ')
            if version_spec:
                # Remove any extra specs like Python version
                version_spec = version_spec.split(';')[0].strip()
                sub_deps[dep_name] = version_spec
            else:
                sub_deps[dep_name] = 'Any'
    
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving sub-dependencies for {package_name}: {e}")
    
    return sub_deps




def version_satisfies(installed_version, required_version):
    """
    Check if the installed version satisfies the required version specifier.
    """
    if ';' in required_version:
        required_version, _ = required_version.split(';', 1)

    try:
        specifier = SpecifierSet(required_version.strip())
    except InvalidSpecifier as e:
        print(f"Invalid specifier: {e}")
        return False
    
    # Compare the installed version with the required version specifier
    return packaging.version.parse(installed_version) in specifier
