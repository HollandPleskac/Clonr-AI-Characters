#!/bin/bash

# Get the operating system name using `uname`
os_name=$(uname -s)

python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./embedding/app/pb \
    --pyi_out=./embedding/app/pb \
    --grpc_python_out=./embedding/app/pb \
    embed.proto

# Check if the operating system is Mac (Darwin) or Linux
# Differs only by sed -i '' vs sed -i
if [[ "$os_name" == "Darwin" ]]; then
    find embedding/app/pb/ -type f -name "*.py" -print0 -exec sed -i '' -e 's/^\(import.*pb2\)/from . \1/g' {} \;
else
    find embedding/app/pb/ -type f -name "*.py" -print0 -exec sed -i -e 's/^\(import.*pb2\)/from . \1/g' {} \;
fi

touch embedding/app/pb/__init__.py

# do the same thing for the app
python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./backend/pb \
    --pyi_out=./backend/pb \
    --grpc_python_out=./backend/pb \
    embed.proto

# Check if the operating system is Mac (Darwin) or Linux
# Differs only by sed -i '' vs sed -i
if [[ "$os_name" == "Darwin" ]]; then
    find backend/pb/ -type f -name "*.py" -print0 -exec sed -i '' -e 's/^\(import.*pb2\)/from . \1/g' {} \;
else
    find backend/pb/ -type f -name "*.py" -print0 -exec sed -i -e 's/^\(import.*pb2\)/from . \1/g' {} \;
fi

touch backend/pb/__init__.py