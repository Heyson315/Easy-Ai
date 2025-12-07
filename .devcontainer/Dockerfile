FROM mcr.microsoft.com/devcontainers/python:0-3.11

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends wget apt-transport-https ca-certificates gnupg \
    && wget -q https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb -O /tmp/packages-microsoft-prod.deb \
    && dpkg -i /tmp/packages-microsoft-prod.deb || true \
    && apt-get update \
    && apt-get install -y --no-install-recommends powershell \
    && apt-get install -y --no-install-recommends curl lsb-release gnupg ca-certificates apt-transport-https \
    && curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg || true \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" > /etc/apt/sources.list.d/azure-cli.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends azure-cli \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/packages-microsoft-prod.deb

# Create workspace and set as working dir
WORKDIR /workspace

# Copy requirements so they can be installed at build time
COPY requirements-extensions.txt requirements.txt /workspace/
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Install Python dependencies
RUN python -m pip install --upgrade pip setuptools wheel && \
    if [ -f /workspace/requirements-extensions.txt ]; then pip install -r /workspace/requirements-extensions.txt; fi && \
    if [ -f /workspace/requirements.txt ]; then pip install -r /workspace/requirements.txt; fi

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["python", "src/extensions/mcp/server.py"]
