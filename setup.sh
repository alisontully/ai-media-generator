#!/bin/bash

if [[ -z "${ENV_NAME}" || -z "${PYTHON_VERSION}" ]]; then
  echo "ENV_NAME and PYTHON_VERSION must be set."
  echo "Usage: ENV_NAME=<env_name> PYTHON_VERSION=<python_version> [PROJECT_NAME=<project_name>] ./setup.sh"
  exit 1
fi

PROJECT_NAME="${PROJECT_NAME:-ai-media-generator}"

echo "Creating a conda environment: ${ENV_NAME} with Python ${PYTHON_VERSION}"
conda create --name "${ENV_NAME}" python="${PYTHON_VERSION}" -y

echo "Activating Conda environment: ${ENV_NAME}"
source activate "${ENV_NAME}"

echo "Installing Poetry in conda environment: ${ENV_NAME}"
conda run -n "${ENV_NAME}" bash -c 'curl -sSL https://install.python-poetry.org | python -'

# Get the environment path
ENV_PATH=$(conda info --envs | grep "${ENV_NAME}" | awk '{print $NF}')

echo "Installing packages from pyproject.toml"
conda run -n "${ENV_NAME}" bash -c "export PATH=\"\${PATH}:${ENV_PATH}/bin:\${HOME}/.local/bin\" && \
  sed 's/^python = .*/python = \"^${PYTHON_VERSION}\"/g' pyproject.toml > tmpfile && mv tmpfile pyproject.toml && \
  sed 's/^name = .*/name = \"${PROJECT_NAME}\"/g' pyproject.toml > tmpfile && mv tmpfile pyproject.toml && \
  poetry lock && poetry install"

echo "Installing pre-commit hooks"
conda run -n "${ENV_NAME}" bash -c "export PATH=\"\${PATH}:${ENV_PATH}/bin:\${HOME}/.local/bin\" && \
  poetry run pre-commit install --allow-missing-config"

echo "Installing the code repository as a Python package"
conda run -n "${ENV_NAME}" bash -c "pip install -e ."

echo "Adding poetry.lock to Git repository"
git add poetry.lock

echo "Setup complete! Your environment ${ENV_NAME} is ready for development."
