import os
import pytest
import click
from astrix.features.class_heirarchy import generate_class_hierarchy


@pytest.fixture
def valid_class_file(tmp_path):
    """Fixture to create a valid Python class file."""
    content = '''
class Base:
    def base_method(self):
        pass

class Derived(Base):
    def derived_method(self):
        pass
    '''
    file_path = tmp_path / "valid_class.py"
    file_path.write_text(content)
    return file_path


def test_generate_class_hierarchy_valid(valid_class_file):
    """Test with a valid Python class file."""
    
    generate_class_hierarchy(valid_class_file)
    
    # Check if the output file is created
    output_path = str(valid_class_file).replace(".py", "_class_graph.png")
    assert os.path.isfile(output_path), "Class Heirarchy image file was not created."

    os.remove(output_path)

def test_generate_class_hierarchy_syntax_error(tmp_path):
    """Test with a Python file that has a syntax error."""
    syntax_error_file = tmp_path / "syntax_error.py"
    syntax_error_file.write_text("class InvalidClass(:\n    pass\n")

    
    with pytest.raises(click.exceptions.Abort):  # Expecting click.Abort() to raise SystemExit
        generate_class_hierarchy(syntax_error_file)
        


def test_generate_class_hierarchy_file_read_error(tmp_path):
    """Test with a non-existent file."""
    non_existent_file = tmp_path / "non_existent_file.py"

    with pytest.raises(click.exceptions.Abort):  # Expecting click.Abort() to raise SystemExit
        generate_class_hierarchy(non_existent_file)



def test_generate_class_hierarchy_empty_file(tmp_path):
    """Test with an empty Python file."""
    empty_file = tmp_path / "empty_file.py"
    empty_file.write_text("")

    with pytest.raises(click.exceptions.Abort):  # Expecting click.Abort() to raise SystemExit
        generate_class_hierarchy(empty_file)



def test_generate_class_hierarchy_file_with_no_classes(tmp_path):
    """Test with a valid Python file that contains no classes."""
    no_classes_file = tmp_path / "no_classes.py"
    content = '''
def standalone_function():
    pass
    '''
    no_classes_file.write_text(content)
    output_file = str(no_classes_file).replace(".py", "_class_graph.png")

    with pytest.raises(click.exceptions.Abort):
        generate_class_hierarchy(no_classes_file)
    
    # Check if the output file is created
    assert not os.path.exists(output_file), "Output file was not created, because there were no classes in the Python file."
