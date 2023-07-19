#!/bin/bash

# Get the operating system name using `uname`
os_name=$(uname -s)


python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./embedding/pb \
    --pyi_out=./embedding/pb \
    --grpc_python_out=./embedding/pb \
    embed.proto

# Check if the operating system is Mac (Darwin) or Linux
# Differs only by sed -i '' vs sed -i
if [[ "$os_name" == "Darwin" ]]; then
    find embedding/pb/ -type f -name "*.py" -print0 -exec sed -i '' -e 's/^\(import.*pb2\)/from . \1/g' {} \;
else
    find embedding/pb/ -type f -name "*.py" -print0 -exec sed -i -e 's/^\(import.*pb2\)/from . \1/g' {} \;
fi

touch embedding/pb/__init__.py