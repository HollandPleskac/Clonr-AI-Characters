#!/bin/bash

# Check if the input file is provided as an argument
set -e
echo "generating client"

npm run generate-client

echo "running node fix"
node fix.ts

# Input file
input_file="./src/client/core/OpenAPI.ts"

# Temporary file to store modified content
temp_file="${input_file}.temp"

# Perform the replacement using sed
sed "s/BASE: '',/BASE: 'http:\/\/localhost:8000',/g" "$input_file" > "$temp_file"
sed "s/WITH_CREDENTIALS: false,WITH_CREDENTIALS: true,/g" "$input_file" > "$temp_file"

# Perform the replacement for WITH_CREDENTIALS using sed
# sed "s/WITH_CREDENTIALS: false,/WITH_CREDENTIALS: true,/g" "$input_file" > "$temp_file"

# Replace the original file with the modified content
mv "$temp_file" "$input_file"

echo "Replacement complete."