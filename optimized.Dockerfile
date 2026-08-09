# SeleniumBase Docker Image - Optimized
FROM ubuntu:24.04
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ENV PYTHONUNBUFFERED=1 PYTHONIOENCODING=UTF-8 DEBIAN_FRONTEND=noninteractive
ENV TZ=America/New_York LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8

#=============================
# Install System Dependencies
#=============================
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata locales \
    fonts-liberation fonts-dejavu-core fonts-noto-color-emoji \
    ca-certificates curl wget unzip vim sudo xvfb xdg-utils x11vnc \
    dbus-x11 libatk1.0-0 libatspi2.0-0 libdbus-1-3 libdrm2 libgtk-3-0 \
    libnspr4 libasound2t64 libu2f-udev libwayland-client0 libx11-6 \
    libx11-xcb1 libxdamage1 libxfixes3 libxkbcommon0 libvulkan1 \
    libnss3 libatk-bridge2.0-0 libcups2 libxcomposite1 libxrandr2 libgbm1 \
    libpango-1.0-0 libcairo2 software-properties-common && \
    sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && locale-gen en_US.UTF-8 && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

#================
# Install Python
#================
RUN add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update && apt-get install -y --no-install-recommends \
    python3.13 python3.13-venv python3.13-dev python3.13-tk build-essential && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.13 1 && \
    python3.13 -m venv /opt/venv && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV PATH="/opt/venv/bin:$PATH"

#================
# Install Chrome
#================
RUN apt-get update && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O /tmp/chrome.deb && \
    apt-get install -y /tmp/chrome.deb && \
    rm /tmp/chrome.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

#=====================
# Set up SeleniumBase
#=====================
COPY sbase /SeleniumBase/sbase/
COPY seleniumbase /SeleniumBase/seleniumbase/
COPY integrations /SeleniumBase/integrations/
COPY examples /SeleniumBase/examples/
COPY requirements.txt setup.py MANIFEST.in pytest.ini setup.cfg virtualenv_install.sh /SeleniumBase/
WORKDIR /SeleniumBase

#===================
# Install Python Packages
#===================
RUN /opt/venv/bin/pip install --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip install -r requirements.txt --no-cache-dir && \
    /opt/venv/bin/pip install . --no-cache-dir && \
    /opt/venv/bin/pip install pyautogui playwright --no-cache-dir && \
    seleniumbase get chromedriver --path && \
    find . -name '*.pyc' -type f -delete && \
    find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

#==============
# Extra config
#==============
ENV DISPLAY=":99"

#==========================================
# Create entrypoint and grab example tests
#==========================================
COPY integrations/docker/docker-entrypoint.sh /docker-entrypoint.sh
COPY integrations/docker/run_docker_test_in_chrome.sh /SeleniumBase/run_docker_test_in_chrome.sh

RUN apt-get update && apt-get install -y dos2unix && apt-get clean && rm -rf /var/lib/apt/lists/* && \
    dos2unix /docker-entrypoint.sh /SeleniumBase/run_docker_test_in_chrome.sh && \
    chmod +x /docker-entrypoint.sh /SeleniumBase/run_docker_test_in_chrome.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["/bin/bash"]
