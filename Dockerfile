FROM python:3.14-alpine AS builder
WORKDIR /app
RUN pip install uv
COPY uv.lock pyproject.toml .
RUN uv export --no-dev --format requirements.txt --no-hashes --no-header --no-annotate > requirements.txt


FROM python:3.14-alpine

# Set work directory
WORKDIR /app

COPY --from=builder /app/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN rm -rf /root/.cache
RUN rm -rf /temp/*
RUN rm -rf /app/requirements.txt

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Copy the source code into the container.
COPY ./app /app

# Expose port
EXPOSE 8000

# Run application.
CMD ["fastapi", "run", "main.py", "--host=0.0.0.0"]