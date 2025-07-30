# WhisperAI Docker Setup

## 🐳 **Docker Configuration**

This project includes Docker configuration for easy deployment and development.

## 📁 **Docker Files**

- `Dockerfile.backend` - Backend API container
- `Dockerfile.frontend` - Frontend Next.js container  
- `Dockerfile` - Single container with both services
- `docker-compose.yml` - Multi-container orchestration
- `docker-start.sh` - Startup script for single container
- `.dockerignore` - Excludes unnecessary files from build

## 🚀 **Quick Start**

### **Option 1: Multi-Container Setup (Recommended)**

1. **Set up environment variables:**
```bash
cp env.example .env
# Edit .env with your API keys
```

2. **Build and run with Docker Compose:**
```bash
docker-compose up --build
```

3. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### **Option 2: Single Container Setup**

1. **Build the container:**
```bash
docker build -t whisperai .
```

2. **Run the container:**
```bash
docker run -p 3000:3000 -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e PINECONE_API_KEY=your_key \
  whisperai
```

## 🔧 **Environment Variables**

Create a `.env` file with the following variables:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Pinecone Configuration  
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=transcription

# Chunking Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📊 **Container Architecture**

### **Multi-Container Setup:**
```
┌─────────────────┐    ┌─────────────────┐
│  Frontend       │    │  Backend        │
│  (Port 3000)    │◄──►│  (Port 8000)    │
│  Next.js        │    │  FastAPI        │
└─────────────────┘    └─────────────────┘
```

### **Single Container Setup:**
```
┌─────────────────────────────────────────┐
│  WhisperAI Container                   │
│  ├── Frontend (Port 3000)             │
│  └── Backend (Port 8000)              │
└─────────────────────────────────────────┘
```

## 🛠️ **Docker Commands**

### **Build and Run:**
```bash
# Build all services
docker-compose build

# Run in background
docker-compose up -d

# Run with logs
docker-compose up

# Stop services
docker-compose down
```

### **Individual Services:**
```bash
# Build backend only
docker build -f Dockerfile.backend -t whisperai-backend .

# Build frontend only  
docker build -f Dockerfile.frontend -t whisperai-frontend .

# Run backend only
docker run -p 8000:8000 whisperai-backend

# Run frontend only
docker run -p 3000:3000 whisperai-frontend
```

### **Development:**
```bash
# Run with volume mounts for development
docker-compose -f docker-compose.dev.yml up

# View logs
docker-compose logs -f

# Access container shell
docker-compose exec whisperai-backend bash
docker-compose exec whisperai-frontend sh
```

## 📁 **Volume Mounts**

The containers use volume mounts for persistent data:

- `./uploads:/app/uploads` - File uploads
- `./temp:/app/temp` - Temporary processing files

## 🔍 **Health Checks**

Both containers include health checks:

- **Backend**: `http://localhost:8000/health`
- **Frontend**: `http://localhost:3000`

## 🐛 **Troubleshooting**

### **Common Issues:**

1. **Port conflicts:**
```bash
# Check if ports are in use
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000
```

2. **API key issues:**
```bash
# Check environment variables
docker-compose exec whisperai-backend env | grep API
```

3. **Build failures:**
```bash
# Clean build
docker-compose down
docker system prune -f
docker-compose build --no-cache
```

4. **Memory issues:**
```bash
# Increase Docker memory limit in Docker Desktop
# Recommended: 4GB+ for Whisper models
```

### **Logs:**
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs whisperai-backend
docker-compose logs whisperai-frontend

# Follow logs in real-time
docker-compose logs -f
```

## 🔒 **Security Considerations**

- **API Keys**: Store securely in `.env` file (not in Dockerfile)
- **Network**: Services communicate over internal Docker network
- **Volumes**: File uploads persist in mounted volumes
- **Health Checks**: Monitor service availability

## 📈 **Performance**

### **Resource Requirements:**
- **CPU**: 2+ cores recommended
- **Memory**: 4GB+ for Whisper models
- **Storage**: 10GB+ for models and uploads
- **Network**: Stable internet for API calls

### **Optimizations:**
- **Model Caching**: Whisper models cached in container
- **Multi-stage Builds**: Optimized image sizes
- **Layer Caching**: Efficient dependency installation
- **Health Checks**: Automatic service monitoring

## 🚀 **Production Deployment**

### **Environment Variables:**
```bash
# Production environment
NODE_ENV=production
PYTHONUNBUFFERED=1
```

### **Security:**
```bash
# Use secrets management
docker secret create openai_key ./openai_key.txt
docker secret create pinecone_key ./pinecone_key.txt
```

### **Scaling:**
```bash
# Scale backend for high load
docker-compose up --scale whisperai-backend=3
```

## 📚 **Additional Resources**

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Docker Guide](https://fastapi.tiangolo.com/deployment/docker/)
- [Next.js Docker Guide](https://nextjs.org/docs/deployment#docker-image)

## 🎯 **Next Steps**

1. **Set up environment variables** in `.env`
2. **Build and run** with `docker-compose up --build`
3. **Access the application** at http://localhost:3000
4. **Test the API** at http://localhost:8000/docs
5. **Upload files** and test transcription features