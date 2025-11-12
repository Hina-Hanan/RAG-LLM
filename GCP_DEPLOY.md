# Deploy to Google Cloud Platform (GCP) - Alternative to Render

Since Render free tier has memory limitations, GCP offers better options for deploying with local embeddings.

## Why GCP?

- ✅ **More RAM**: Cloud Run free tier includes 512MB-2GB RAM (configurable)
- ✅ **Local Embeddings**: Can use sentence-transformers without memory issues
- ✅ **Free Tier**: Generous free tier with $300 credit
- ✅ **Better Performance**: No cold starts like Render free tier
- ✅ **Scalable**: Auto-scales based on traffic

## Prerequisites

1. Google Cloud account (sign up at https://cloud.google.com)
2. Google Cloud SDK installed locally
3. Docker installed (for containerization)

## Option 1: Cloud Run (Recommended - Serverless)

### Step 1: Install Google Cloud SDK

```bash
# Windows (PowerShell)
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe

# Or use Chocolatey
choco install gcloudsdk

# Mac/Linux
curl https://sdk.cloud.google.com | bash
```

### Step 2: Authenticate and Set Project

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud auth configure-docker
```

### Step 3: Create Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install sentence-transformers for local embeddings
RUN pip install sentence-transformers>=2.2.0

# Copy application code
COPY . .

# Expose port (Cloud Run uses PORT env var)
ENV PORT=8080
EXPOSE 8080

# Run the application
CMD exec uvicorn app:app --host 0.0.0.0 --port $PORT
```

### Step 4: Update requirements.txt

Make sure `sentence-transformers` is included:

```txt
fastapi>=0.104.0
uvicorn>=0.24.0
langchain>=0.1.0
langchain-google-genai>=0.0.6
langchain-community>=0.0.10
langchain-core>=0.1.23
langchain-text-splitters>=0.0.1
langchain-classic>=1.0.0
faiss-cpu>=1.9.0
pypdf>=3.17.0
python-docx>=1.1.0
python-dotenv>=1.0.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
sentence-transformers>=2.2.0
```

### Step 5: Create .env file for Cloud Run

Set environment variables in Cloud Run:

```bash
# Set environment variables
gcloud run deploy rag-chatbot \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --set-env-vars "LLM_PROVIDER=gemini,EMBEDDING_PROVIDER=local,MODEL_NAME=gemini-2.5-flash,GOOGLE_API_KEY=your_key,VECTOR_STORE_PATH=./vector_store,DOCUMENTS_PATH=./documents,TOP_K_RESULTS=7"
```

Or use Secret Manager for API keys:

```bash
# Create secret
echo -n "your-api-key" | gcloud secrets create google-api-key --data-file=-

# Deploy with secret
gcloud run deploy rag-chatbot \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --update-secrets GOOGLE_API_KEY=google-api-key:latest
```

### Step 6: Build and Deploy

```bash
# Build and deploy to Cloud Run
gcloud run deploy rag-chatbot \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10
```

### Step 7: Access Your App

After deployment, you'll get a URL like:
```
https://rag-chatbot-xxxxx-uc.a.run.app
```

## Option 2: App Engine (Traditional)

### Step 1: Create app.yaml

```yaml
runtime: python311

instance_class: F2  # 256MB RAM (F4 = 512MB, F4_1G = 1GB)

env_variables:
  LLM_PROVIDER: "gemini"
  EMBEDDING_PROVIDER: "local"
  MODEL_NAME: "gemini-2.5-flash"
  GOOGLE_API_KEY: "your-key-here"
  VECTOR_STORE_PATH: "./vector_store"
  DOCUMENTS_PATH: "./documents"
  TOP_K_RESULTS: "7"

automatic_scaling:
  min_instances: 0
  max_instances: 10
```

### Step 2: Deploy

```bash
gcloud app deploy
```

## Option 3: Compute Engine VM (Full Control)

### Step 1: Create VM

```bash
gcloud compute instances create rag-chatbot-vm \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=20GB
```

### Step 2: SSH and Setup

```bash
gcloud compute ssh rag-chatbot-vm --zone=us-central1-a

# On VM:
sudo apt update
sudo apt install python3-pip python3-venv git -y
git clone YOUR_REPO_URL
cd ragllm
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install sentence-transformers

# Create systemd service
sudo nano /etc/systemd/system/rag-chatbot.service
```

Service file:
```ini
[Unit]
Description=RAG Chatbot API
After=network.target

[Service]
User=YOUR_USER
WorkingDirectory=/home/YOUR_USER/ragllm
Environment="PATH=/home/YOUR_USER/ragllm/venv/bin"
ExecStart=/home/YOUR_USER/ragllm/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable rag-chatbot
sudo systemctl start rag-chatbot
```

## Configuration for Local Embeddings

### Update .env for GCP

```env
LLM_PROVIDER=gemini
EMBEDDING_PROVIDER=local  # Can use local on GCP!
MODEL_NAME=gemini-2.5-flash
GOOGLE_API_KEY=your_key_here
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
VECTOR_STORE_PATH=./vector_store
DOCUMENTS_PATH=./documents
TOP_K_RESULTS=7
```

## Cost Comparison

### Render Free Tier
- RAM: 512MB (limited)
- Cold starts: Yes (15 min timeout)
- Cost: Free (with limitations)

### GCP Cloud Run Free Tier
- RAM: 512MB-2GB (configurable)
- Requests: 2 million/month free
- CPU: 180,000 vCPU-seconds/month free
- Cost: Free tier + pay-as-you-go after

### GCP Compute Engine
- e2-micro: Always free (limited)
- e2-small: ~$6/month
- e2-medium: ~$24/month (2GB RAM, perfect for local embeddings)

## Recommended: Cloud Run with 2GB RAM

Best balance of cost and performance:

```bash
gcloud run deploy rag-chatbot \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300
```

This gives you:
- ✅ 2GB RAM (enough for sentence-transformers)
- ✅ Local embeddings (no API quota issues)
- ✅ Auto-scaling
- ✅ Pay only for what you use
- ✅ No cold starts (with min-instances=1, but costs more)

## Next Steps

1. **Choose deployment option** (Cloud Run recommended)
2. **Update requirements.txt** to include sentence-transformers
3. **Set EMBEDDING_PROVIDER=local** in environment variables
4. **Deploy and test**

## Troubleshooting

**Issue: Out of memory**
- Increase memory: `--memory 2Gi` or `--memory 4Gi`

**Issue: Slow startup**
- Pre-build vector store and include in Docker image
- Use Cloud Run with min-instances=1 (costs more)

**Issue: API key security**
- Use Secret Manager instead of env vars
- Never commit API keys to Git

## Resources

- Cloud Run Docs: https://cloud.google.com/run/docs
- App Engine Docs: https://cloud.google.com/appengine/docs
- Compute Engine Docs: https://cloud.google.com/compute/docs
- GCP Free Tier: https://cloud.google.com/free

