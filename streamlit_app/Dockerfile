FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set working directory
WORKDIR /app

# Install system dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy workspace configuration from root
COPY ../pyproject.toml /workspace/
COPY ../uv.lock* /workspace/

# Copy streamlit app workspace
COPY pyproject.toml .
COPY . .

# Install dependencies using uv (from workspace root)
WORKDIR /workspace
RUN uv sync --frozen --no-dev

# Back to app directory
WORKDIR /app

# Copy database (or mount as volume in production)
# COPY ../ferrodata.duckdb /app/ferrodata.duckdb

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run Streamlit using uv
ENTRYPOINT ["uv", "run", "--directory", "/workspace", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
