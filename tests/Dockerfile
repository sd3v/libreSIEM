FROM python:3.12-slim

WORKDIR /app

# Copy source code
COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# Install package in development mode
RUN pip install -e .

# Set environment variables
ENV PYTHONPATH=/app

# Default command
CMD ["pytest", "tests/integration/", "-v"]
