from radon.visitors import ComplexityVisitor
from radon.complexity import cc_visit
from radon.metrics import mi_parameters
from tabulate import tabulate
import click
import os



def analyze_code_quality(path):
    path = str(path)
    path = path or click.get_current_context().params['path']
    if not path.lower().endswith('.py'):
        click.secho(f"Error: The file '{path}' does not have a '.py' extension.", fg='red')
        raise click.Abort()

    if not os.path.isfile(path):
        click.secho(f"Error: The path '{path}' is not a file or does not exist.", fg='red')
        raise click.Abort()
    
    try:
        with open(path, 'r', encoding='utf-8') as file:
            code = file.read()
    except IOError as e:
        click.secho(f"Error: Unable to read the file '{path}'. {e}", fg='red')
        raise click.Abort()
    
    results = cc_visit(code)
    return results


def analyze_maintainability_index(path, multi):
    """Calculate the maintainability index of the given Python file."""
    path = str(path)
    path = path or click.get_current_context().params['path']

    if not path.lower().endswith('.py'):
        click.secho(f"Error: The file '{path}' does not have a '.py' extension.", fg='red')
        raise click.Abort()

    if not os.path.isfile(path):
        click.secho(f"Error: The path '{path}' is not a file or does not exist.", fg='red')
        raise click.Abort()

    try:
        with open(path, 'r', encoding='utf-8') as file:
            code = file.read()
    except IOError as e:
        click.secho(f"Error: Unable to read the file '{path}'. {e}", fg='red')
        raise click.Abort()
    
    maintainability_data = list(mi_parameters(code, multi))
    keys = ["Halstead Volume", "Complexity", "LLOC", "Percentage of comments"]

    maintainability_data = [[val] for val in maintainability_data]
    data = dict(zip(keys, maintainability_data))
    return data



