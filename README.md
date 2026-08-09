# Build and Run
```bash
docker build -f Dockerfile -t flight-sniper .
docker build -t flight-sniper .
# --rm removes the container once it exits
docker run --rm flight-sniper
docker run seleniumbase ./run_docker_test_in_chrome.sh
```

# Install Deps
```bash
python -m venv .venv
pip install --no-cache-dir -r requirements.txt
```

## Stealthy
YT: https://www.youtube.com/watch?v=DMKlh_-gdGs

SeleniumBase on GitHub: https://github.com/seleniumbase/SeleniumBase

Dockerfile: https://github.com/seleniumbase/SeleniumBase/blob/master/Dockerfile

Docker instructions: https://github.com/seleniumbase/SeleniumBase/blob/master/integrations/docker/ReadMe.md

CDP Mode: https://github.com/seleniumbase/SeleniumBase/blob/master/examples/cdp_mode/ReadMe.md

Stealthy Playwright Mode: https://github.com/seleniumbase/SeleniumBase/blob/master/examples/cdp_mode/playwright/ReadMe.md