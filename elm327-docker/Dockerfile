FROM python:3.11-slim

WORKDIR /app

# Copy emulator source
COPY emulator/ /app/

# Install system build tools (needed for python-daemon etc)
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install the emulator package
RUN pip install --no-cache-dir .

# Expose TCP port
EXPOSE 35000

# Run emulator as module
CMD ["python", "-m", "elm", "-n", "35000", "-s", "car"]