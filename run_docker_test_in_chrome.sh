#!/bin/bash
set -e
# Run example test from inside Docker image
echo "Running example SeleniumBase test from Docker with headless Chrome..."
pytest my_first_test.py --browser=chrome --headless
exec "$@"
