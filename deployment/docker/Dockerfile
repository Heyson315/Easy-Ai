# M365 Security Toolkit - Production Container
# Multi-stage build for optimized production deployment

# Stage 1: Build environment with PowerShell and Python
FROM mcr.microsoft.com/powershell:lts-windowsservercore-ltsc2022 AS build

# Set working directory
WORKDIR /app

# Install Python 3.11
RUN powershell -Command \
    "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe' -OutFile 'python-installer.exe'; \
    Start-Process -FilePath 'python-installer.exe' -ArgumentList '/quiet', 'InstallAllUsers=1', 'PrependPath=1' -Wait; \
    Remove-Item 'python-installer.exe'"

# Install Git for potential repository operations
RUN powershell -Command \
    "Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe' -OutFile 'git-installer.exe'; \
    Start-Process -FilePath 'git-installer.exe' -ArgumentList '/SILENT' -Wait; \
    Remove-Item 'git-installer.exe'"

# Copy application files
COPY . /app/

# Install Python dependencies
RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt
RUN python -m pip install -r requirements-dev.txt

# Install PowerShell modules
RUN powershell -Command \
    "Set-PSRepository -Name PSGallery -InstallationPolicy Trusted; \
    Install-Module -Name ExchangeOnlineManagement -Scope AllUsers -Force; \
    Install-Module -Name Microsoft.Graph.Authentication -Scope AllUsers -Force; \
    Install-Module -Name Microsoft.Graph.Identity.SignIns -Scope AllUsers -Force; \
    Install-Module -Name Microsoft.Graph.Identity.DirectoryManagement -Scope AllUsers -Force; \
    Install-Module -Name Microsoft.Graph.Users -Scope AllUsers -Force; \
    Install-Module -Name Microsoft.Online.SharePoint.PowerShell -Scope AllUsers -Force; \
    Install-Module -Name Az.KeyVault -Scope AllUsers -Force; \
    Install-Module -Name Az.Storage -Scope AllUsers -Force"

# Stage 2: Production runtime
FROM mcr.microsoft.com/powershell:lts-windowsservercore-ltsc2022 AS runtime

# Set working directory
WORKDIR /app

# Install Python runtime (minimal)
RUN powershell -Command \
    "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe' -OutFile 'python-installer.exe'; \
    Start-Process -FilePath 'python-installer.exe' -ArgumentList '/quiet', 'InstallAllUsers=1', 'PrependPath=1' -Wait; \
    Remove-Item 'python-installer.exe'"

# Copy application and dependencies from build stage
COPY --from=build /app /app
COPY --from=build ["C:/Program Files/PowerShell/Modules", "C:/Program Files/PowerShell/Modules"]
COPY --from=build ["C:/Python311", "C:/Python311"]

# Create application user (security best practice)
RUN powershell -Command \
    "New-LocalUser -Name 'm365toolkit' -Description 'M365 Security Toolkit Service Account' -NoPassword; \
    Add-LocalGroupMember -Group 'Users' -Member 'm365toolkit'"

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PSModulePath="C:\Program Files\PowerShell\Modules;C:\Program Files\WindowsPowerShell\Modules"

# Configure application settings
ENV M365_TOOLKIT_ENV=production
ENV M365_TOOLKIT_CONFIG_PATH=/app/config/production_config.json
ENV M365_TOOLKIT_LOG_LEVEL=Information

# Create directories for data and logs
RUN powershell -Command \
    "New-Item -ItemType Directory -Path 'C:\app\data' -Force; \
    New-Item -ItemType Directory -Path 'C:\app\logs' -Force; \
    New-Item -ItemType Directory -Path 'C:\app\output' -Force; \
    New-Item -ItemType Directory -Path 'C:\app\temp' -Force"

# Set proper permissions
RUN powershell -Command \
    "icacls 'C:\app' /grant 'm365toolkit:(OI)(CI)F' /T"

# Health check script
COPY deployment/docker/healthcheck.ps1 /app/healthcheck.ps1
HEALTHCHECK --interval=300s --timeout=30s --start-period=60s --retries=3 \
    CMD powershell -File /app/healthcheck.ps1

# Expose port for potential web interface (future)
EXPOSE 8080

# Set user context
USER m365toolkit

# Default command - run the audit scheduler
CMD ["powershell", "-File", "/app/scripts/powershell/Start-M365ToolkitService.ps1"]