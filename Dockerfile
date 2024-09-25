# Stage 1: Builder
FROM python:3-alpine AS builder

WORKDIR /app

# Set up virtual environment
RUN python3 -m venv venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies
COPY SpotifyEarlyWrapped/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runner
FROM python:3-alpine AS runner

WORKDIR /app

# Copy the virtual environment and application code
COPY --from=builder /app/venv venv
COPY SpotifyEarlyWrapped/ .  
# Copy the contents of your SpotifyEarlyWrapped folder

ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV FLASK_APP=app.py  
#Since app.py is in the root of /app now

# Expose the correct port
EXPOSE 5000  
# Match the port you’re using locally

# Run the application with Gunicorn
CMD ["gunicorn", "--bind", ":5000", "--workers", "2", "app:app"]
