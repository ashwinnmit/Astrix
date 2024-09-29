import click
import networkx as nx
import matplotlib.pyplot as plt
import ast


def generate_class_hierarchy(path):
    """Generate a class hierarchy for the given Python script."""
    try:
        with open(path, 'r') as file:
            code = file.read()
    except Exception as e:
        click.echo(f"Error reading file: {e}")
        raise click.Abort()

    if not code.strip():
        click.secho(f"Error: The path '{path}' is an empty python file", fg='yellow')
        raise click.Abort()
    
    output_path = str(path).replace(".py", "_class_graph.png")
    # Parse the code
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        click.secho(f"Error: The python file '{path}' has Syntax Errors", fg='red')
        raise click.Abort()
    graph = nx.DiGraph()
    classes_found = False

    # Traverse the AST and build the class hierarchy
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes_found = True
            class_name = node.name
            graph.add_node(class_name, type='class')
            
            # Add methods as nodes
            for body_node in node.body:
                if isinstance(body_node, ast.FunctionDef):
                    method_name = body_node.name
                    graph.add_node(f"{class_name}.{method_name}", type='method')
                    graph.add_edge(class_name, f"{class_name}.{method_name}")
            
            # Add inheritance edges
            if node.bases:
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        base_class = base.id
                        graph.add_edge(base_class, class_name)
                    elif isinstance(base, ast.Attribute):
                        base_class = f"{base.value.id}.{base.attr}"
                        graph.add_edge(base_class, class_name)



    if not classes_found:
        click.secho(f"Error: The file '{path}' does not contain any class definitions.", fg='red')
        raise click.Abort()
    # Draw the graph
    pos = nx.spring_layout(graph)  # Seed for reproducibility
    node_colors = ['skyblue' if data['type'] == 'class' else 'lightgreen' for _, data in graph.nodes(data=True)]
    nx.draw(graph, pos, with_labels=True, node_size=3000, node_color=node_colors, font_size=10, font_weight="bold", arrows=True)
    plt.title("Class Hierarchy")
    plt.savefig(output_path)
    click.echo("Class hierarchy saved as class_hierarchy.png")

