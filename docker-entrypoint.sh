#!/bin/bash
set -e
echo "***** SeleniumBase Docker Machine *****"
/SeleniumBase/run_docker_test_in_chrome.sh
exec "$@"
