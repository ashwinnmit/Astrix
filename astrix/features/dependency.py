import click
import ast
import requests
from stdlib_list import in_stdlib
from importlib.metadata import packages_distributions

def fetch_module_details(url):
    """
    Fetches the description of a given Python package using the PyPI API.
    
    :param package_name: The name of the package.
    :return: Description of the package or an error message if not found.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching package information : {e}")
        return {}
    except KeyError:
        print(f'Package not found or no description available')
        return {}

def processResponse(project_url):
    github_url = ""

    for value in project_url.values():
        if 'github' in value.lower():
            github_url = value
            break
    
    return github_url

def get_pypi_name(module):
    res = packages_distributions()
    if module not in res:
        return module
    else:
        return res[module][0]


def generate_dependency_info(path):
    """Generate a dependency graph for the specified Python script."""
    try:
        with open(path, 'r') as file:
            code = file.read()
    except Exception as e:
        click.echo(f"Error reading file: {e}")
        raise click.Abort()
    
    
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        click.secho(f"Error: The python file '{path}' has Syntax Errors", fg='red')
        raise click.Abort()
    

    modules = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name
                    if in_stdlib(module):
                        documentation = f"https://docs.python.org/3/library/{module}.html"
                        modules[module] = ["Inbuilt module of python", documentation, "https://github.com/python/cpython"]

                    else:
                        module = get_pypi_name(module)
                        url = f"https://pypi.org/pypi/{module}/json"
                        moduleDetails = fetch_module_details(url)
                        if moduleDetails == {}:
                            summary = "No summary available :("
                            project_urls = {}
                            documentation = "No documentation available :("
                            github_url = "No github URL :("
                        else:
                            summary = moduleDetails["info"].get("summary", "No summary available :(")
                            project_urls = moduleDetails["info"].get("project_urls", {})
                            documentation = project_urls.get("Documentation", f"https://pypi.org/pypi/{module}")
                            github_url = processResponse(project_urls)
                        modules[module] = [summary, documentation, github_url]
                    

            elif isinstance(node, ast.ImportFrom):
                module = node.module
                if in_stdlib(module):
                    documentation = f"https://docs.python.org/3/library/{module}.html"
                    modules[module] = ["Inbuilt module of python", documentation, "https://github.com/python/cpython"]
                else:
                    module = get_pypi_name(module)
                    url = f"https://pypi.org/pypi/{module}/json"
                    moduleDetails = fetch_module_details(url)
                    if moduleDetails == {}:
                            summary = "No summary available :("
                            project_urls = {}
                            documentation = "No documentation available :("
                            github_url = "No github URL :("
                    else:
                        summary = moduleDetails["info"].get("summary", "No summary available :(")
                        project_urls = moduleDetails["info"].get("project_urls", {})
                        documentation = project_urls.get("Documentation", f"https://pypi.org/pypi/{module}")
                        github_url = processResponse(project_urls)
                    modules[module] = [summary, documentation, github_url]

    
    table = []
    if(modules == {}):
        return table
    
    for pkg, info in modules.items():
        table.append([pkg, *info])
    
    return table

    
    
    