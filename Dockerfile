FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Add Microsoft repository and install ODBC driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends \
    msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# Find and configure the actual ODBC driver location
RUN find / -name "libmsodbcsql-18*.so*" 2>/dev/null | while read -r file; do \
    echo "[ODBC Driver 18 for SQL Server]" > /etc/odbcinst.ini && \
    echo "Driver=$file" >> /etc/odbcinst.ini && \
    echo "Setup=$file" >> /etc/odbcinst.ini; \
    done

# Verify ODBC setup
RUN odbcinst -j && \
    cat /etc/odbcinst.ini

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY azure_data_loader.py .

CMD ["python", "azure_data_loader.py"]