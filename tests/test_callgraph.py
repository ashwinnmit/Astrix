import os
import pytest
import click
from astrix.features.callgraph import generate_call_graph

@pytest.fixture
def sample_python_file(tmp_path):
    """Fixture that provides a temporary Python file for testing."""
    content = '''
def main():
    helper()

def helper():
    print("Hello, World!")
    '''
    # Create a temporary file and write the content
    file_path = tmp_path / "sample_python_file.py"
    file_path.write_text(content)
    
    return file_path


def test_generate_call_graph_valid_file(sample_python_file):
    """Test with a valid Python file."""
    # Call the function to generate the call graph
    generate_call_graph(sample_python_file)

    # Check if the call graph image file was created
    output_path = str(sample_python_file).replace(".py", "_callgraph.png")
    assert os.path.isfile(output_path), "Call graph image file was not created."

    # Clean up the created image file
    os.remove(output_path)

def test_generate_call_graph_file_read_error(tmp_path):
    """Test with a non-existent file."""
    path = str(tmp_path / "non_existent_file.py")

    with pytest.raises(click.exceptions.Abort):
        generate_call_graph(path)


def test_generate_call_graph_empty_file(tmp_path):
    """Test with an empty Python file."""
    empty_file = tmp_path / "empty_file.py"
    empty_file.write_text("")

    with pytest.raises(click.exceptions.Abort):
        generate_call_graph(empty_file)



def test_generate_call_graph_invalid_file(tmp_path):
    """Test with an invalid Python file."""
    invalid_file = tmp_path / "invalid_file.py"
    invalid_file.write_text("print(Hello World)") 

    with pytest.raises(click.exceptions.Abort):
        generate_call_graph(invalid_file)
