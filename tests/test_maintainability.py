import os
import pytest
import click
from astrix.features.code_quality import analyze_maintainability_index



@pytest.fixture
def sample_python_file(tmp_path):
    """Fixture that provides a temporary Python file for testing."""
    content = '''
import requests
import json
import os
from pandas import DataFrame


def get_package_requirements(package_name):
    """Fetch the package metadata from PyPI and return required dependencies."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    data = response.json()

    requirements = data.get('info', {}).get('requires_dist', [])
    
    return requirements

def parse_requirements(requirements):
    """Parse the requirements list into a dictionary."""
    parsed = {}
    for requirement in requirements:
        pkg_name, _, version_spec = requirement.partition(' ')
        parsed[pkg_name] = version_spec or 'Any'
    
    return parsed

# Example usage
package_name = 'pandas'
requirements = get_package_requirements(package_name)
parsed_requirements = parse_requirements(requirements)

print(f"Dependencies required by {package_name}:")
for pkg, version in parsed_requirements.items():
    print(f"{pkg}: {version}")

    '''
    # Create a temporary file and write the content
    file_path = tmp_path / "sample_python_file.py"
    file_path.write_text(content)
    
    return file_path




def test_analyze_maintainability_index_valid_file(sample_python_file):
    """Test with a valid Python file."""
    multi = False  # Change as necessary for your function's requirements
    result = analyze_maintainability_index(sample_python_file, multi)
    
    # Check that the result contains expected keys
    expected_keys = ["Halstead Volume", "Complexity", "LLOC", "Percentage of comments"]
    assert all(key in result for key in expected_keys)



def test_analyze_maintainability_index_invalid_extension():
    """Test with a non-Python file."""
    path = "invalid_file.txt"
    multi = False

    with pytest.raises(click.exceptions.Abort):  # click.Abort() raises SystemExit
        analyze_maintainability_index(path, multi)


def test_analyze_maintainability_index_non_existent_file():
    """Test with a non-existent file."""
    path = "non_existent_file.py"
    multi = False

    with pytest.raises(click.exceptions.Abort):  # click.Abort() raises SystemExit
        analyze_maintainability_index(path, multi)


def test_analyze_maintainability_index_unreadable_file(tmp_path):
    """Test with an unreadable file."""
    # Create a temporary file and change permissions to make it unreadable
    unreadable_file = tmp_path / "unreadable.py"
    unreadable_file.write_text("print('Hello, World!')\n")
    os.remove(unreadable_file)  # Set permissions to 000

    multi = False

    with pytest.raises(click.exceptions.Abort):  # Expecting a SystemExit due to an unreadable file
        analyze_maintainability_index(unreadable_file, multi)