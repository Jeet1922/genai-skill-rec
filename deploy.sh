#!/bin/bash

# SkillRec Deployment Script
# This script builds Docker images and deploys to Kubernetes

set -e  # Exit on any error

echo "🚀 Starting SkillRec deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install kubectl first."
        exit 1
    fi
    
    if ! command -v minikube &> /dev/null; then
        print_warning "minikube is not installed. Installing for local development..."
        # You can add minikube installation here if needed
    fi
    
    print_status "Prerequisites check completed."
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Build backend image
    print_status "Building backend image..."
    docker build -f Dockerfile.backend -t skillrec-backend:latest .
    
    # Build frontend image
    print_status "Building frontend image..."
    docker build -f Dockerfile.frontend -t skillrec-frontend:latest .
    
    print_status "Docker images built successfully."
}

# Deploy to Kubernetes
deploy_to_k8s() {
    print_status "Deploying to Kubernetes..."
    
    # Create namespace
    kubectl apply -f k8s/namespace.yaml
    
    # Apply ConfigMap
    kubectl apply -f k8s/configmap.yaml
    
    # Apply Secret (you need to update this with your actual API key)
    print_warning "Please update k8s/secret.yaml with your actual GROQ_API_KEY before proceeding."
    read -p "Have you updated the secret? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl apply -f k8s/secret.yaml
    else
        print_error "Please update the secret and run the script again."
        exit 1
    fi
    
    # Deploy backend
    kubectl apply -f k8s/backend-deployment.yaml
    
    # Deploy frontend
    kubectl apply -f k8s/frontend-deployment.yaml
    
    # Create services
    kubectl apply -f k8s/services.yaml
    
    # Create ingress (optional - for external access)
    kubectl apply -f k8s/ingress.yaml
    
    print_status "Kubernetes deployment completed."
}

# Check deployment status
check_status() {
    print_status "Checking deployment status..."
    
    echo "Namespace:"
    kubectl get namespace skillrec
    
    echo -e "\nPods:"
    kubectl get pods -n skillrec
    
    echo -e "\nServices:"
    kubectl get services -n skillrec
    
    echo -e "\nDeployments:"
    kubectl get deployments -n skillrec
    
    echo -e "\nIngress:"
    kubectl get ingress -n skillrec
}

# Wait for pods to be ready
wait_for_pods() {
    print_status "Waiting for pods to be ready..."
    
    kubectl wait --for=condition=ready pod -l app=skillrec-backend -n skillrec --timeout=300s
    kubectl wait --for=condition=ready pod -l app=skillrec-frontend -n skillrec --timeout=300s
    
    print_status "All pods are ready!"
}

# Show access information
show_access_info() {
    print_status "Deployment completed successfully!"
    echo -e "\n${GREEN}Access Information:${NC}"
    echo "Frontend: http://localhost (if using LoadBalancer)"
    echo "Backend API: http://localhost:8000 (if using NodePort)"
    echo -e "\nTo check logs:"
    echo "kubectl logs -f deployment/skillrec-backend -n skillrec"
    echo "kubectl logs -f deployment/skillrec-frontend -n skillrec"
    echo -e "\nTo scale deployments:"
    echo "kubectl scale deployment skillrec-backend --replicas=3 -n skillrec"
    echo "kubectl scale deployment skillrec-frontend --replicas=3 -n skillrec"
}

# Main execution
main() {
    check_prerequisites
    build_images
    deploy_to_k8s
    wait_for_pods
    check_status
    show_access_info
}

# Run main function
main "$@" 