#!/bin/bash
# This script wraps pip to intercept and block pandas installations

# Log the command
echo "PIP WRAPPER: $@" >> /tmp/pip_wrapper.log

# Check if this is an install command
if [[ "$1" == "install" ]]; then
  # Check if pandas is being installed
  if echo "$@" | grep -i "pandas" > /dev/null; then
    echo "BLOCKED: Attempted to install pandas" >> /tmp/pip_wrapper.log
    echo "ERROR: pandas installation blocked by pip_wrapper.sh"
    exit 1
  fi
  
  # If installing from a requirements file, check and clean it first
  for arg in "$@"; do
    if [[ "$arg" == "-r" || "$arg" == "--requirement" ]]; then
      # Get the next argument which should be the requirements file
      req_file="${@[$((i+1))]}"
      if [ -f "$req_file" ]; then
        echo "Checking requirements file: $req_file" >> /tmp/pip_wrapper.log
        cat "$req_file" >> /tmp/pip_wrapper.log
        
        # Create a clean version without pandas
        grep -v -i "pandas" "$req_file" > "${req_file}.clean"
        mv "${req_file}.clean" "$req_file"
        
        echo "Cleaned requirements file: $req_file" >> /tmp/pip_wrapper.log
        cat "$req_file" >> /tmp/pip_wrapper.log
      fi
    fi
    i=$((i+1))
  done
fi

# Execute the original pip command
/usr/bin/pip "$@"
