@echo off

rem ================== Setup python environment ===================

rem Option to accept a custom Python path
set /p python_executable="Enter the path to the Python executable (leave blank for default): "

rem Set the name of the virtual environment
set venv_name=venv

rem Set the path to the requirements.txt file
set requirements_file=requirements.txt

rem If a custom Python path is not provided, use the default python executable
if "%python_executable%"=="" (
    set python_executable=python
)

rem Create a virtual environment
%python_executable% -m venv %venv_name%

rem Activate the virtual environment
call %venv_name%\Scripts\activate

rem Install dependencies from requirements.txt
pip install -r %requirements_file%

echo Virtual environment created and activated. Dependencies installed.
echo To deactivate the virtual environment, run: deactivate