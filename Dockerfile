FROM node:20-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies and Azure CLI (with verification)
RUN set -ex && \
    apt-get update && \
    apt-get install -y \
        ca-certificates \
        curl \
        apt-transport-https \
        lsb-release \
        gnupg \
        python3 \
        python3-pip \
        netcat-openbsd \
    && mkdir -p /etc/apt/keyrings \
    && curl -sLS https://packages.microsoft.com/keys/microsoft.asc | \
        gpg --dearmor | \
        tee /etc/apt/keyrings/microsoft.gpg > /dev/null \
    && chmod go+r /etc/apt/keyrings/microsoft.gpg \
    && AZ_REPO=$(lsb_release -cs) \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | \
        tee /etc/apt/sources.list.d/azure-cli.list \
    && apt-get update \
    && apt-get install -y azure-cli \
    && az --version \
    && rm -rf /var/lib/apt/lists/*

    
# Install npm@11.4.2
RUN npm install -g npm@11.4.2

# Install Playwright@1.53.0 with dependencies
RUN npx -y playwright@1.53.0 install --with-deps

# Copy requirements.txt first for better cache utilization
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copy the rest of the application
COPY src/ /app/src/

# Copy start.sh to the container
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose port 8080
EXPOSE 8080

# Command to run the application and MCP server
CMD ["/start.sh"]