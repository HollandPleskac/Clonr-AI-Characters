set -x
set -e

# Sort imports one per line, so autoflake can remove unused imports
isort --recursive  --force-single-line-imports --apply .
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place . --exclude=__init__.py

# linting
black .
isort --profile black .
flake8 --ignore E201,E501,W605,W503,W291,E741 --exclude="pb/*","*__init__.py"
