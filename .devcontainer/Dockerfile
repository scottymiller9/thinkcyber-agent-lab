# Student environment: Python + the standard tools the agent orchestrates.
# Works in GitHub Codespaces and locally (VS Code "Reopen in Container").
FROM mcr.microsoft.com/devcontainers/python:3.12

# Standard, off-the-shelf security tooling the agent calls.
#   nmap     - port/service scanning
#   nikto    - web server scanner (optional extra)
#   whatweb  - web stack fingerprinting
#   sqlmap   - SQL injection testing
#   ffuf     - content discovery (installed via go/apt depending on base)
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
        nmap nikto whatweb sqlmap ffuf \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# If 'ffuf' isn't in apt on your base image, uncomment to fetch the binary:
# RUN curl -sSL https://github.com/ffuf/ffuf/releases/latest/download/ffuf_linux_amd64.tar.gz \
#     | tar -xz -C /usr/local/bin ffuf

WORKDIR /workspace
