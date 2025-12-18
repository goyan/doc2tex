@echo off
echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -e ".[all]"

echo.
echo Setup complete! Virtual environment is active.
echo.
echo To activate later, run: venv\Scripts\activate
echo To run tests: python -m pytest
echo To run the tool: docx2latex --help
