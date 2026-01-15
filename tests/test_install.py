import pytest
from unittest import mock
import toml
import os
from astrix.features.conflict_management import parse_pyprojecttoml, installTxt, installSetup, create_venv, delete_venv, list_venvs
import shutil

def test_parse_pyprojecttoml():
    mock_toml_content = {
        'tool': {
            'poetry': {
                'dependencies': {
                    'requests': '^2.25.1',
                    'flask': '^1.1.2',
                }
            }
        }
    }
    
    with mock.patch('builtins.open', mock.mock_open(read_data=toml.dumps(mock_toml_content))):
        dependencies = parse_pyprojecttoml('pyproject.toml')
        assert dependencies == {
            'requests': '^2.25.1',
            'flask': '^1.1.2'
        }


def test_installTxt():
    with open('requirements.txt', 'w') as f:
        f.write('requests==2.25.1\nflask==1.1.2\n# Comment\n\n')

    result = installTxt('requirements.txt')
    assert result == {'requests': '2.25.1', 'flask': '1.1.2'}

    os.remove('requirements.txt')




def test_installSetup():
    setup_content = """
from setuptools import setup

setup(
    name='test_package',
    install_requires=[
        'requests==2.25.1',
        'flask==1.1.2',
    ],
)
"""
    with open('setup.py', 'w') as f:
        f.write(setup_content)

    result = installSetup('setup.py')
    assert result == {'requests': '2.25.1', 'flask': '1.1.2'}

    os.remove('setup.py')




def test_create_venv_already_exists():
    env_name = 'existing_env'
    
    # Create the environment directory
    os.makedirs(env_name, exist_ok=True)

    with mock.patch('subprocess.check_call') as mock_check_call:
        create_venv(env_name, {})
        mock_check_call.assert_not_called()  # Should not call check_call if it exists

    shutil.rmtree(env_name)  # Cleanup



def test_create_venv_creates_new_env():
    env_name = 'new_env'
    
    with mock.patch('os.path.exists', return_value=False), \
         mock.patch('subprocess.check_call') as mock_check_call:
        
        create_venv(env_name, {})
        mock_check_call.assert_called_once_with([mock.ANY, "-m", "venv", env_name])
    
    # Cleanup
    if os.path.exists(env_name):
        shutil.rmtree(env_name)


def test_create_venv_installs_dependencies():
    env_name = 'new_env'
    deps = {'requests': '2.25.1'}
    
    with mock.patch('os.path.exists', return_value=False), \
         mock.patch('subprocess.check_call') as mock_check_call:
        
        create_venv(env_name, deps)
        
        # Verify virtual environment creation
        mock_check_call.assert_any_call([mock.ANY, "-m", "venv", env_name])
        
        # Verify installation of dependencies
        for dep in deps:
            mock_check_call.assert_any_call([mock.ANY, "-m", "pip", "install", dep])
    
    # Cleanup
    if os.path.exists(env_name):
        shutil.rmtree(env_name)



def test_delete_venv():
    env_name = 'to_delete_env'
    os.makedirs(env_name, exist_ok=True)  # Create the environment directory
    
    delete_venv(env_name)
    assert not os.path.exists(env_name)  # Ensure the directory is deleted




def test_list_venvs_no_recorded_envs(monkeypatch):
    monkeypatch.setattr('os.path.exists', lambda x: False)
    
    with mock.patch('builtins.open', side_effect=FileNotFoundError):
        from io import StringIO
        import sys

        captured_output = StringIO()
        sys.stdout = captured_output
        list_venvs()
        sys.stdout = sys.__stdout__

        assert "No virtual environments have been recorded." in captured_output.getvalue()
