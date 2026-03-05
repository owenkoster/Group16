FROM python:3.11-slim

WORKDIR /app

# Copy emulator source
COPY emulator/ /app/

# Install system build tools needed for python-daemon
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install the emulator package
RUN pip install --no-cache-dir .

# Default environment variables
ENV PORT=35000
ENV SCENARIO=car

# Expose TCP port
EXPOSE $PORT

# Run emulator with configurable scenario and port
CMD ["sh", "-c", "python -m elm -n $PORT -s $SCENARIO"]