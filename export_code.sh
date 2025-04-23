#!/bin/bash

# This script is optimized for React TypeScript projects.
# Place this script in the root folder of your project.
# Run the command chmod +x get_code_context.sh
# Execute with ./get_code_context.sh

# Use the current directory as the project directory
project_dir=$(pwd)

# Use a fixed name for the output file in the current directory
output_file="${project_dir}/code_context.txt"

# Check if the output file exists and remove it if it does
if [ -f "$output_file" ]; then
  rm "$output_file"
fi

# List of directories to look for
directories=()

# List of specific files to include
specific_files=("animal_manager.py" "animal.py" "building.py" "components.py" "economy_manager.py" "game_state.py" "main.py" "terrain.py" "tourist.py" "ui.py" "vehicle.py")

# List of file types to ignore
ignore_files=("*.ico" "*.png" "*.jpg" "*.jpeg" "*.gif" "*.svg" "*.pyc")

# List of files to exclude (provide relative paths from the project root)
exclude_files=()

# Function to append file content
append_file_content() {
  local file_path=$1
  local relative_path=${file_path#"$project_dir/"}
  echo "// File: $relative_path" >> "$output_file"
  cat "$file_path" >> "$output_file"
  echo "" >> "$output_file"
}

# Recursive function to read files and append their content
read_files() {
  for entry in "$1"/*
  do
    if [ -d "$entry" ]; then
      # If entry is a directory, call this function recursively
      read_files "$entry"
    elif [ -f "$entry" ]; then
      # Compute the file's relative path from the project root
      local relative_path=${entry#"$project_dir/"}
      
      # Check if the file is in the exclusion list
      should_exclude=false
      for exclude_pattern in "${exclude_files[@]}"; do
        if [[ "$relative_path" == $exclude_pattern ]]; then
          should_exclude=true
          break
        fi
      done

      if $should_exclude; then
        continue
      fi

      # Check if the file type should be ignored
      should_ignore=false
      for ignore_pattern in "${ignore_files[@]}"; do
        if [[ "$entry" == $ignore_pattern ]]; then
          should_ignore=true
          break
        fi
      done

      # If the file is not ignored, append its content
      if ! $should_ignore; then
        append_file_content "$entry"
      fi
    fi
  done
}

# Call the recursive function for each specified directory in the project directory
for dir in "${directories[@]}"; do
  if [ -d "${project_dir}/${dir}" ]; then
    read_files "${project_dir}/${dir}"
  fi
done

# Append specific files mentioned in the specific_files array
for file in "${specific_files[@]}"; do
  if [ -f "${project_dir}/${file}" ]; then
    append_file_content "${project_dir}/${file}"
  fi
done
