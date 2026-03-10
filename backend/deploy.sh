#!/bin/bash
# ============================================
# IMOOGLE 5.0 - Deployment Script
# For DigitalOcean Droplet
# ============================================

set -e

echo "🚀 Deploying Imoogle 5.0..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root${NC}"
    exit 1
fi

# Update system
echo -e "${YELLOW}Updating system packages...${NC}"
apt-get update && apt-get upgrade -y

# Install Docker if not installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
fi

# Install Docker Compose if not installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Installing Docker Compose...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Create app directory
APP_DIR=/opt/imoogle
mkdir -p $APP_DIR
cd $APP_DIR

# Copy files (assuming they're in current directory or use git)
echo -e "${YELLOW}Setting up application files...${NC}"

# If using git:
# git clone https://github.com/your-repo/imoogle.git .
# Or copy files manually

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${RED}.env file not found!${NC}"
    echo -e "${YELLOW}Please create .env file from .env.example${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Edit the .env file with your credentials, then run this script again${NC}"
    exit 1
fi

# Create SSL directory
mkdir -p ssl

# Check for SSL certificates
if [ ! -f ssl/fullchain.pem ]; then
    echo -e "${YELLOW}SSL certificates not found. Setting up Let's Encrypt...${NC}"
    
    # Install certbot
    apt-get install -y certbot
    
    # Get domain from user
    read -p "Enter your domain name: " DOMAIN
    
    # Stop any running services on port 80
    docker-compose down 2>/dev/null || true
    
    # Get certificate
    certbot certonly --standalone -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
    
    # Copy certificates
    cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem ssl/
    cp /etc/letsencrypt/live/$DOMAIN/privkey.pem ssl/
    
    # Update nginx.conf with domain
    sed -i "s/your-domain.com/$DOMAIN/g" nginx.conf
    
    echo -e "${GREEN}SSL certificates configured!${NC}"
fi

# Build and start containers
echo -e "${YELLOW}Building and starting containers...${NC}"
docker-compose build --no-cache
docker-compose up -d

# Wait for services to start
echo -e "${YELLOW}Waiting for services to start...${NC}"
sleep 10

# Check health
echo -e "${YELLOW}Checking service health...${NC}"
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ Imoogle 5.0 is running!${NC}"
else
    echo -e "${RED}❌ Service health check failed${NC}"
    docker-compose logs imoogle
    exit 1
fi

# Set up automatic certificate renewal
echo -e "${YELLOW}Setting up certificate auto-renewal...${NC}"
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet && docker-compose restart nginx") | crontab -

# Set up log rotation
cat > /etc/logrotate.d/imoogle << EOF
/opt/imoogle/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        docker-compose -f /opt/imoogle/docker-compose.yml restart imoogle
    endscript
}
EOF

# Print summary
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  IMOOGLE 5.0 DEPLOYED SUCCESSFULLY! 🎉${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "📍 Application URL: https://$DOMAIN"
echo -e "📍 Webhook URL: https://$DOMAIN/webhook"
echo -e "📍 Health Check: https://$DOMAIN/health"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Set your Telegram webhook:"
echo "   curl -X POST 'https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://$DOMAIN/webhook'"
echo ""
echo "2. Test your bot by sending /start"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "  docker-compose logs -f imoogle  # View logs"
echo "  docker-compose restart          # Restart services"
echo "  docker-compose down              # Stop services"
echo ""
