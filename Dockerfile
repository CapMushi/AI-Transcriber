# # Multi-stage build for development
# FROM python:3.12-slim as backend

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     ffmpeg \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# WORKDIR /app

# # Copy and install Python dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy backend source
# COPY api/ ./api/
# COPY src/ ./src/
# COPY config.py .
# COPY api_server.py .
# COPY main.py .

# # Create upload directories
# RUN mkdir -p /app/uploads /app/temp

# # Frontend stage
# FROM node:18-alpine as frontend

# WORKDIR /app/frontend

# # Copy frontend dependencies
# COPY frontend/package*.json ./
# RUN npm install --legacy-peer-deps

# # Copy frontend source
# COPY frontend/ .

# # Build frontend
# RUN npm run build

# # Final stage
# FROM python:3.11-slim

# # Install system dependencies including Node.js
# RUN apt-get update && apt-get install -y \
#     ffmpeg \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# # Install Node.js
# RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
#     && apt-get install -y nodejs

# WORKDIR /app

# # Copy Python dependencies
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy backend source
# COPY api/ ./api/
# COPY src/ ./src/
# COPY config.py .
# COPY api_server.py .
# COPY main.py .

# # Copy built frontend from frontend stage
# COPY --from=frontend /app/frontend/.next ./frontend/.next
# COPY --from=frontend /app/frontend/public ./frontend/public
# COPY --from=frontend /app/frontend/package*.json ./frontend/

# # Install frontend dependencies
# WORKDIR /app/frontend
# RUN npm install --only=production --legacy-peer-deps


# # Expose ports
# EXPOSE 8000 3000

# # Set environment variables
# ENV PYTHONPATH=/app
# ENV PYTHONUNBUFFERED=1
# ENV NODE_ENV=production

# # Copy startup script
# COPY docker-start.sh /app/
# RUN chmod +x /app/docker-start.sh

# # Start both services
# CMD ["/app/docker-start.sh"]

FROM python:3.12-slim as backend-build

WORKDIR /app

# Install backend build dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY api/ ./api/
COPY src/ ./src/
COPY config.py .
COPY api_server.py .
COPY main.py .

# Create upload directories
RUN mkdir -p /app/uploads /app/temp


# ---------- Frontend Build Stage ----------
FROM node:18-alpine as frontend-build

WORKDIR /app/frontend

# Install frontend dependencies and build
COPY frontend/package*.json ./
RUN npm install --legacy-peer-deps

COPY frontend/ .
RUN npm run build


# ---------- Final Runtime Image ----------
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy backend from build stage
COPY --from=backend-build /app /app

# Copy built frontend assets only
COPY --from=frontend-build /app/frontend/.next ./frontend/.next
COPY --from=frontend-build /app/frontend/public ./frontend/public
COPY --from=frontend-build /app/frontend/package*.json ./frontend/

# Environment setup
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

# Expose backend and frontend ports
EXPOSE 8000 3000

# Copy startup script
COPY docker-start.sh /app/
RUN chmod +x /app/docker-start.sh

# Start services
CMD ["/app/docker-start.sh"]