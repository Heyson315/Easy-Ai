# M365 Security Toolkit - Production Container
FROM python:3.11-slim

LABEL maintainer="M365 Security Toolkit Team"
LABEL version="1.0.0"
LABEL description="M365 Security and SharePoint Analysis Toolkit"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Install PowerShell
RUN wget -q https://packages.microsoft.com/config/debian/11/packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && apt-get update \
    && apt-get install -y powershell \
    && rm packages-microsoft-prod.deb

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY config/ ./config/

# Create necessary directories
RUN mkdir -p /app/data/raw /app/data/processed /app/data/archive \
    /app/output/reports/security /app/output/reports/business \
    /app/output/reports/academic /app/output/reports/financial \
    /app/output/dashboards /app/output/presentations /app/output/automated

# Set permissions
RUN chmod +x scripts/powershell/*.ps1

# Install PowerShell modules (in container)
RUN pwsh -Command "Set-PSRepository -Name PSGallery -InstallationPolicy Trusted; \
    Install-Module -Name Microsoft.Graph.Authentication -Scope AllUsers -Force; \
    Install-Module -Name Microsoft.Graph.Identity.SignIns -Scope AllUsers -Force; \
    Install-Module -Name Microsoft.Graph.Identity.DirectoryManagement -Scope AllUsers -Force; \
    Install-Module -Name Microsoft.Graph.Users -Scope AllUsers -Force; \
    Install-Module -Name ExchangeOnlineManagement -Scope AllUsers -Force; \
    Install-Module -Name Microsoft.Online.SharePoint.PowerShell -Scope AllUsers -Force"

# Create non-root user
RUN useradd -m -u 1000 m365user && chown -R m365user:m365user /app
USER m365user

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["python", "-m", "src.core.app"]