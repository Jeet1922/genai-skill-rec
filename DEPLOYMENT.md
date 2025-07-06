# SkillRec Deployment Guide

This guide covers deploying the SkillRec application using Docker and Kubernetes with various hosting options.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development with Docker Compose](#local-development)
3. [Production Deployment with Docker Compose](#production-docker)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Free/Open Source Hosting Options](#hosting-options)
6. [Monitoring and Scaling](#monitoring)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools
- Docker and Docker Compose
- kubectl (for Kubernetes deployment)
- A GROQ API key

### Optional Tools
- minikube (for local Kubernetes testing)
- helm (for advanced Kubernetes deployments)

## Local Development with Docker Compose

### Quick Start
```bash
# Clone the repository
git clone <your-repo-url>
cd AI+Skill+Rec

# Set your GROQ API key
export GROQ_API_KEY="your-groq-api-key"

# Start the application
docker-compose up --build

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8000
```

### Development Commands
```bash
# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up --build --force-recreate
```

## Production Deployment with Docker Compose

### Simple Production Setup
```bash
# Set environment variables
export GROQ_API_KEY="your-groq-api-key"

# Deploy with production configuration
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

### With SSL/HTTPS
```bash
# Create SSL certificates (self-signed for testing)
mkdir ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/nginx.key -out ssl/nginx.crt

# Deploy with SSL
docker-compose -f docker-compose.prod.yml --profile ssl up -d
```

## Kubernetes Deployment

### Local Kubernetes (minikube)

#### 1. Start minikube
```bash
# Start minikube with enough resources
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable ingress addon
minikube addons enable ingress

# Point your shell to minikube's docker-daemon
eval $(minikube docker-env)
```

#### 2. Prepare Secrets
```bash
# Update the secret with your GROQ API key
# Edit k8s/secret.yaml and replace <BASE64_ENCODED_GROQ_API_KEY>
echo -n "your-groq-api-key" | base64
# Copy the output and update k8s/secret.yaml
```

#### 3. Deploy
```bash
# Make the deployment script executable
chmod +x deploy.sh

# Run the deployment
./deploy.sh

# Or deploy manually
kubectl apply -f k8s/
```

#### 4. Access the Application
```bash
# Get the minikube IP
minikube ip

# Access the application
# Frontend: http://<minikube-ip>
# Backend: http://<minikube-ip>:8000
```

### Cloud Kubernetes (Free Tiers)

#### Google Cloud Platform (GKE)
```bash
# Install gcloud CLI
# Create a free GKE cluster
gcloud container clusters create skillrec-cluster \
  --zone=us-central1-a \
  --num-nodes=1 \
  --machine-type=e2-micro \
  --disk-size=10

# Get credentials
gcloud container clusters get-credentials skillrec-cluster --zone=us-central1-a

# Deploy
./deploy.sh
```

#### DigitalOcean Kubernetes
```bash
# Install doctl CLI
# Create a cluster (free tier available)
doctl kubernetes cluster create skillrec-cluster \
  --region=nyc1 \
  --size=s-1vcpu-1gb \
  --count=1

# Deploy
./deploy.sh
```

#### Linode Kubernetes Engine (LKE)
```bash
# Install linode-cli
# Create a cluster
linode-cli lke cluster-create \
  --label skillrec-cluster \
  --region us-east \
  --k8s_version 1.25 \
  --node_pools.type g6-standard-1 \
  --node_pools.count 1

# Deploy
./deploy.sh
```

## Free/Open Source Hosting Options

### 1. Railway.app (Free Tier)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

### 2. Render.com (Free Tier)
- Connect your GitHub repository
- Set environment variables (GROQ_API_KEY)
- Deploy automatically on push

### 3. Fly.io (Free Tier)
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Create app
fly apps create skillrec

# Deploy
fly deploy
```

### 4. Heroku (Free Tier Discontinued, but Affordable)
```bash
# Install Heroku CLI
# Create Procfile
echo "web: uvicorn api.main:app --host=0.0.0.0 --port=\$PORT" > Procfile

# Deploy
heroku create skillrec-app
heroku config:set GROQ_API_KEY=your-key
git push heroku main
```

### 5. Oracle Cloud Free Tier
- 2 AMD-based Compute VMs
- 24GB memory
- Perfect for Kubernetes deployment

## Monitoring and Scaling

### Health Checks
```bash
# Check pod health
kubectl get pods -n skillrec

# View logs
kubectl logs -f deployment/skillrec-backend -n skillrec
kubectl logs -f deployment/skillrec-frontend -n skillrec

# Check service endpoints
kubectl get endpoints -n skillrec
```

### Scaling
```bash
# Scale backend
kubectl scale deployment skillrec-backend --replicas=3 -n skillrec

# Scale frontend
kubectl scale deployment skillrec-frontend --replicas=3 -n skillrec

# Auto-scaling (requires metrics server)
kubectl autoscale deployment skillrec-backend \
  --cpu-percent=70 --min=1 --max=5 -n skillrec
```

### Resource Monitoring
```bash
# Install metrics server (if not already installed)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# View resource usage
kubectl top pods -n skillrec
kubectl top nodes
```

## Troubleshooting

### Common Issues

#### 1. Pods Not Starting
```bash
# Check pod status
kubectl describe pod <pod-name> -n skillrec

# Check events
kubectl get events -n skillrec --sort-by='.lastTimestamp'
```

#### 2. API Connection Issues
```bash
# Check if backend is accessible
kubectl port-forward service/skillrec-backend-service 8000:8000 -n skillrec

# Test API
curl http://localhost:8000/api/v1/health
```

#### 3. Frontend Not Loading
```bash
# Check nginx configuration
kubectl exec -it <frontend-pod> -n skillrec -- nginx -t

# Check nginx logs
kubectl logs <frontend-pod> -n skillrec
```

#### 4. Memory Issues
```bash
# Check resource usage
kubectl top pods -n skillrec

# Increase memory limits in deployment files if needed
```

### Logs and Debugging
```bash
# Follow logs in real-time
kubectl logs -f deployment/skillrec-backend -n skillrec

# Execute commands in pods
kubectl exec -it <pod-name> -n skillrec -- /bin/bash

# Check environment variables
kubectl exec <pod-name> -n skillrec -- env | grep GROQ
```

### Cleanup
```bash
# Remove all resources
kubectl delete namespace skillrec

# Remove Docker images
docker rmi skillrec-backend:latest skillrec-frontend:latest

# Clean up Docker Compose
docker-compose down -v
```

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Secrets**: Use Kubernetes secrets for sensitive data
3. **Network Policies**: Implement network policies for pod-to-pod communication
4. **RBAC**: Set up proper role-based access control
5. **SSL/TLS**: Use HTTPS in production

## Performance Optimization

1. **Resource Limits**: Set appropriate CPU and memory limits
2. **Horizontal Pod Autoscaling**: Enable HPA for automatic scaling
3. **Caching**: Implement Redis for caching if needed
4. **CDN**: Use a CDN for static assets
5. **Database**: Consider using a managed database service

## Cost Optimization

1. **Use Spot Instances**: For non-critical workloads
2. **Right-sizing**: Monitor and adjust resource requests
3. **Auto-scaling**: Scale down during low usage
4. **Free Tiers**: Leverage cloud provider free tiers
5. **Reserved Instances**: For predictable workloads

This deployment guide provides multiple options for hosting your SkillRec application, from simple Docker Compose setups to full Kubernetes deployments on various cloud platforms. 