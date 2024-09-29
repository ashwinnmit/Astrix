import click
import ast
import networkx as nx
import matplotlib.pyplot as plt
import os


def generate_call_graph(path):
    """Generate a call graph for the given Python script."""

    if not os.path.isfile(path):
        click.secho(f"Error: The path '{path}' is not a file or does not exist.", fg='red')
        raise click.Abort()
    
    try:
        with open(path, 'r') as file:
            code = file.read()
    except Exception as e:
        click.echo(f"Error reading file: {e}")
        raise click.Abort()

    if not code.strip():
        click.secho(f"Error: The path '{path}' is an empty python file", fg='yellow')
        raise click.Abort()
    
    output_path = str(path).replace(".py", "_callgraph.png")
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        click.secho(f"Error: The python file '{path}' has Syntax Errors", fg='red')
        raise click.Abort()
    graph = nx.DiGraph()

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_name = node.name
            graph.add_node(function_name)
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Name):
                        called_function = child.func.id
                        graph.add_edge(function_name, called_function)

    pos = nx.spring_layout(graph)
    nx.draw(graph, pos, with_labels=True, node_size=2000, node_color="lightblue", font_size=10, font_weight="bold", arrows=True)
    plt.title("Call Graph")
    plt.savefig(output_path)
    click.echo(f"Call graph saved as {output_path}")