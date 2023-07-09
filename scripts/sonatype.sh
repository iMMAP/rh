#!/bin/bash

export PYTHONIOENCODING=utf-8
echo "Check the version of python"
python=$(which python)
echo "$python"

echo "Check the version of pip"
pip=$(which pip)
echo "$pip"

echo "Check if virtual environment is activated"

if [[ "$VIRTUAL_ENV" != "" ]]
then
  echo "Virtual environment is already activated"
else
  echo "Virtual environment is not activated"
  $python -m venv .env
  if [[ "$OSTYPE" == "win32"* ]]; then
    source .env/Scripts/activate
  else
    source .env/bin/activate
  fi

fi

echo "Check if Jake, powered by Sonatype OSS Index is already installed"
# shellcheck disable=SC2143

if [[ ! $(pip list|grep "jake") ]]; then
    pip install jake
fi

echo "Running Jake to check vulnerabilities on local prior to using the layers"

# shellcheck disable=SC1072
if [[ -f "jake_requirements.txt" ]]; then
  echo "File already exists"
  jake ddt -t PIP -f "jake_requirements.txt" --output-format json > report_jake.json
  else
    $($pip freeze > jake_requirements.txt)
        jake ddt -t PIP -f "jake_requirements.txt" --output-format json > report_jake.json
fi

echo "Running Jake to check vulnerabilities on local prior to using the layers"

  sam build
  if [[ -f "jake_requirements_layers.txt" ]]; then
  echo "File already exists"
  jake ddt -t PIP -f "jake_requirements_layers.txt" --output-format json > report_jake_layers.json
  else
    $($pip freeze > jake_requirements_layers.txt)
        jake ddt -t PIP -f "jake_requirements_layers.txt" --output-format json > report_jake_layers.json
fi

echo "END OF SCRIPT"
