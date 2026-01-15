import click
import os
import inspect
from tabulate import tabulate
from radon.visitors import Class
from astrix.features.code_quality import analyze_code_quality
from astrix.features.code_quality import analyze_maintainability_index
from astrix.features.callgraph import generate_call_graph
from astrix.features.dependency import generate_dependency_info
from astrix.features.class_heirarchy import generate_class_hierarchy
from astrix.features.conflict_management import installTxt, installSetup, create_venv, delete_venv, list_venvs

@click.group()
def cli():
    """Astrix - Your All-in-One Python Project Analyzer"""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--path', '-p', type=click.Path(exists=True, file_okay=True, dir_okay=False), help='Path to the Python file')
def analyze(path):
    """ 
    This command analyzes functions in a given Python file and returns details about them, including their name, location, and complexity.



Output Details:

- Name: The name of the function being analyzed. \n
- Line Number: The line number where the function starts. \n
- Column Offset: The column position where the function starts. \n
- Endline: The line number where the function ends. \n
- isMethod: Indicates whether the function is a method (True) or a standalone function (False). \n
- Class: The name of the class the method belongs to, if applicable. Otherwise, it's `None`. \n
- Closures: Any closures (inner functions) within the function. \n
- Complexity: The cyclomatic complexity of the function, which indicates its code complexity level. \n

Example: astrix analyze example_file.py

    \b
    Name                        Line Number    Column Offset    Endline  isMethod    Class    Closures    Complexity
    ------------------------    -------------  ---------------  ---------  ----------  -------  ---------  ------------
    get_package_requirements     6              0                14        False       None     []         1
    parse_requirements           16             0                23        False       None     []         3
    """
    results = analyze_code_quality(path)
    if not results:
        click.secho("No functions found to analyze.", fg='yellow')
        raise click.Abort()
    

    # name, lineno, col_offset, endline, is_method, classname, closures, complexity
    data = []
    for result in results:
        if not isinstance(result, Class):
            res = [result.name, result.lineno, result.col_offset, result.endline, result.is_method, result.classname, result.closures, result.complexity]
            data.append(res)
    
    # print(data)
        
    click.echo(tabulate(data, headers=["Name", "Line Number", "Column Offset", "Endline", "isMethod", "Class", "Closures", "Complexity"], 
                        missingval="None"))
@cli.command()
@click.argument('path', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--path', '-p', type=click.Path(exists=True, file_okay=True, dir_okay=False), help='Path to the Python file')
@click.option('--multi', is_flag=True, help='Include multi-line strings in maintainability index calculation')
def maintainability(path, multi):
    """
This command analyzes the Halstead metrics, complexity, and code structure for functions in a given Python file and returns detailed information about them.

Output Details:

- Halstead Volume: A software metric that represents the volume of the code based on the number of operators and operands in the program. It indicates the size of the implementation. \n
- Complexity: The cyclomatic complexity of the function, representing the number of independent paths through the code. A higher number indicates more complex logic. \n
- LLOC (Logical Lines of Code): The number of executable lines in the function, excluding comments and blank lines. \n
- Percentage of Comments: The proportion of comments in the function relative to the number of lines of code (expressed as a percentage). High values suggest well-documented code. \n

Example: $ astrix analyze-metrics sample.py

    \b
    Halstead Volume    Complexity    LLOC    Percentage of comments
    -----------------  ------------  ------  ------------------------
                    0             1       5                       220

    """
    data = analyze_maintainability_index(path, multi)
    click.echo(tabulate(data, headers=["Halstead Volume", "Complexity", "LLOC", "Percentage of comments"]))


@cli.command()
@click.argument('path', type=click.Path(exists=True, file_okay=True, dir_okay=False))
def callgraph(path):
    """
This command analyzes the specified Python file and generates a call graph that visually represents the function call hierarchy within the code. The call graph is saved as an image file in the same directory as the analyzed Python file.



Output Details:

- A call graph is generated as an image (typically a 'png' format), which visually shows the relationships between functions and how they call each other. \n
- The output file will be saved in the same folder as the program being analyzed, with a name corresponding to the analyzed file (e.g., `sample_callgraph.png` for `sample.py`). \n

Example: $ astrix callgraph sample.py \n

This will generate `sample_callgraph.png` in the same directory as `sample.py`, representing the function call hierarchy.


    """
    generate_call_graph(path)


@cli.command()
@click.argument('path', type=click.Path(exists=True, file_okay=True, dir_okay=False))
def deps(path):
    """
Analyze the specified Python file and return a table of dependencies used within the file, including module names, descriptions, documentation links, and GitHub URLs.

Output Details:

- Module: The name of the imported module. \n
- Description: A brief description of what the module does. \n
- Documentation: A link to the official documentation for the module. \n
- GitHub URL: A link to the GitHub repository for the module. \n

Example: $ astrix deps sample.py

\b
+----------+------------------------------+------------------------------------------+--------------------------------------+
| Module   | Description                  | Documentation                            | GitHub URL                           |
+==========+==============================+==========================================+======================================+
| requests | Python HTTP for Humans.      | https://requests.readthedocs.io          | https://github.com/psf/requests      |
+----------+------------------------------+------------------------------------------+--------------------------------------+
| json     | Inbuilt module of Python     | https://docs.python.org/3/library/json.html | https://github.com/python/cpython    |
+----------+------------------------------+------------------------------------------+--------------------------------------+
| os       | Inbuilt module of Python     | https://docs.python.org/3/library/os.html | https://github.com/python/cpython    |
+----------+------------------------------+------------------------------------------+--------------------------------------+
| pandas   | Powerful data structures for | https://pandas.pydata.org/docs/          | https://github.com/pandas-dev/pandas |
|          | data analysis, time series,  |                                          |                                      |
|          | and statistics               |                                          |                                      |
+----------+------------------------------+------------------------------------------+--------------------------------------+

This command will analyze `sample.py` and return a formatted table of dependencies used in the script.

    """
    table = generate_dependency_info(path)
    headers = ["Module", "Description", "Documentation", "GitHub URL"]

    if len(table) == 0:
        click.echo("No dependencies found in the given file")
    # print(table)
    else:
        click.echo(tabulate(table, headers=headers, maxcolwidths=[10, 30, 40, 40], tablefmt="grid"))
    
    


@cli.command()
@click.argument('path', type=click.Path(exists=True, file_okay=True, dir_okay=False))
def class_info(path):
    """
Analyze the specified Python file and generate a class hierarchy graph that visually represents the relationships between classes defined within the file. The graph will be saved as `userProvidedpath_class_graph.png` in the same directory as the analyzed Python file.

Output Details:

- A class hierarchy graph is created as an image (typically `.png` format), illustrating the parent-child relationships between classes. \n

Example: $ astrix class-info sample.py

This command will analyze `sample.py` and generate `sample_class_graph.png` in the same directory, representing the class hierarchy within the file.

    """
    generate_class_hierarchy(path)


@cli.command()
@click.argument('path', type=click.Path(exists=True, file_okay=True, dir_okay=False), required=False)
def install(path):
    """
Create a virtual environment for the current project and install packages specified in the provided path. If no path is given, only the virtual environment will be created.

Output Details:

- A virtual environment will be created in the current directory. \n
- If a path to a requirements file (e.g., `requirements.txt` or `setup.py`) is provided, all specified packages will be installed in the created virtual environment. \n

Example: 

$ astrix install requirements.txt

This command will create a virtual environment and install all packages listed in `requirements.txt` within that environment.

$ astrix install

This command will create a virtual environment without installing any packages, as no path was provided.

    """
    if path:
        if path.endswith('.txt'):
            deps = installTxt(path)
        elif path.endswith('.setup.py'):
            deps = installSetup(path)
        else:
            click.echo("Unsupported File Format")
            return
    # print(os.path.basename(directory))
    else:
        deps = []

    directory = os.path.dirname(os.path.abspath(path)) if path else os.getcwd()
    create_venv(f"virtual-{os.path.basename(directory)}", deps)

@cli.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False, dir_okay=True))
def delete(path):
    """
Delete the virtual environment associated with the specified Python project. The virtual environment will be removed from the directory where the project file resides.

Output Details:

- The command will permanently delete the virtual environment directory associated with the provided file path. \n


Example:

$ astrix delete /path/to/project/ \n

This command will delete the virtual environment located in the `/path/to/project/` directory.
    """
    #directory = os.path.dirname(os.path.abspath(path))
    delete_venv(f"{os.path.basename(path)}")


if __name__ == '__main__':
    cli()
