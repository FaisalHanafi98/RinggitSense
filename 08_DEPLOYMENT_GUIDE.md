# DuitSedar — Deployment Guide

**Document Version:** 1.0  
**Author:** Mohamad Faisal Bin Mohd Hanafi  
**Created:** January 2026

---

## Table of Contents

1. [Deployment Overview](#1-deployment-overview)
2. [Local Development Setup](#2-local-development-setup)
3. [Docker Configuration](#3-docker-configuration)
4. [AWS Deployment](#4-aws-deployment)
5. [Environment Variables](#5-environment-variables)
6. [CI/CD Pipeline](#6-cicd-pipeline)
7. [Monitoring & Logging](#7-monitoring--logging)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Deployment Overview

### 1.1 Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PRODUCTION ARCHITECTURE                            │
└─────────────────────────────────────────────────────────────────────────────┘

        Internet
            │
            ▼
    ┌───────────────┐
    │   CloudFlare  │  (Optional: CDN + SSL)
    │      DNS      │
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │   AWS EC2     │
    │   t3.micro    │
    │               │
    │ ┌───────────┐ │        ┌───────────────┐
    │ │  Docker   │ │        │   AWS RDS     │
    │ │ Container │ │◄──────►│  PostgreSQL   │
    │ │           │ │        │  db.t3.micro  │
    │ │ Spring    │ │        └───────────────┘
    │ │ Boot +    │ │
    │ │ React     │ │        ┌───────────────┐
    │ └───────────┘ │        │  Claude API   │
    │       │       │◄──────►│  (Anthropic)  │
    └───────┼───────┘        └───────────────┘
            │
            ▼
    ┌───────────────┐
    │    Clerk      │
    │    Auth       │
    └───────────────┘
```

### 1.2 Resource Requirements

| Resource | Development | Production |
|----------|-------------|------------|
| EC2 Instance | - | t3.micro (Free Tier) |
| RDS Instance | - | db.t3.micro (Free Tier) |
| Storage | 20GB | 20GB |
| Memory | 4GB local | 1GB EC2 |
| CPU | 2 cores | 2 vCPU |

---

## 2. Local Development Setup

### 2.1 Prerequisites

```bash
# Required software
- Java 17+ (OpenJDK or Temurin)
- Node.js 18+
- Docker & Docker Compose
- Git
- PostgreSQL 15 (via Docker)
```

### 2.2 Clone and Setup

```bash
# Clone repository
git clone https://github.com/yourusername/duitsedar.git
cd duitsedar

# Copy environment template
cp .env.example .env

# Edit .env with your values
nano .env
```

### 2.3 Start Development Environment

```bash
# Start all services (database, backend, frontend)
docker-compose up -d

# Or start individually:

# 1. Start database only
docker-compose up -d db

# 2. Start backend
cd backend
./gradlew bootRun

# 3. Start frontend
cd frontend
npm install
npm run dev
```

### 2.4 Verify Setup

```bash
# Check database
docker exec -it duitsedar-db psql -U postgres -d duitsedar -c "SELECT 1"

# Check backend health
curl http://localhost:8080/actuator/health

# Check frontend
open http://localhost:5173
```

---

## 3. Docker Configuration

### 3.1 Development Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: pgvector/pgvector:pg15
    container_name: duitsedar-db
    environment:
      POSTGRES_DB: duitsedar
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./backend/src/main/resources/db/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: duitsedar-backend
    environment:
      SPRING_PROFILES_ACTIVE: dev
      DATABASE_URL: jdbc:postgresql://db:5432/duitsedar
      DB_USER: ${DB_USER:-postgres}
      DB_PASSWORD: ${DB_PASSWORD:-postgres}
      CLAUDE_API_KEY: ${CLAUDE_API_KEY}
      CLERK_SECRET_KEY: ${CLERK_SECRET_KEY}
    ports:
      - "8080:8080"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - ~/.gradle:/root/.gradle

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: duitsedar-frontend
    environment:
      VITE_API_URL: http://localhost:8080
      VITE_CLERK_PUBLISHABLE_KEY: ${CLERK_PUBLISHABLE_KEY}
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

volumes:
  pgdata:
```

### 3.2 Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM eclipse-temurin:17-jdk-alpine as builder

WORKDIR /app
COPY gradle gradle
COPY gradlew .
COPY build.gradle .
COPY settings.gradle .
COPY src src

RUN chmod +x gradlew
RUN ./gradlew build -x test

FROM eclipse-temurin:17-jre-alpine

WORKDIR /app
COPY --from=builder /app/build/libs/*.jar app.jar

# Add wait-for-it script for database readiness
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

### 3.3 Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    image: duitsedar:latest
    container_name: duitsedar-app
    environment:
      SPRING_PROFILES_ACTIVE: prod
      DATABASE_URL: ${DATABASE_URL}
      CLAUDE_API_KEY: ${CLAUDE_API_KEY}
      CLERK_SECRET_KEY: ${CLERK_SECRET_KEY}
    ports:
      - "80:8080"
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 4. AWS Deployment

### 4.1 AWS Resources to Create

```
1. EC2 Instance (t3.micro - Free Tier)
2. RDS PostgreSQL (db.t3.micro - Free Tier)
3. Security Groups
4. Elastic IP (Optional)
5. S3 Bucket (for backups - Optional)
```

### 4.2 EC2 Setup

```bash
# Connect to EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# Update system
sudo yum update -y

# Install Docker
sudo amazon-linux-extras install docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login again for docker group
exit
ssh -i your-key.pem ec2-user@your-ec2-ip

# Verify installation
docker --version
docker-compose --version
```

### 4.3 RDS Setup

```bash
# Create RDS PostgreSQL instance via AWS Console:
# 1. Go to RDS → Create database
# 2. Choose PostgreSQL 15
# 3. Select Free tier
# 4. Set DB instance identifier: duitsedar-db
# 5. Set master username and password
# 6. Configure VPC to allow EC2 access
# 7. Note the endpoint URL

# Enable pgvector extension (connect from EC2)
psql -h your-rds-endpoint -U postgres -d duitsedar
CREATE EXTENSION vector;
\q
```

### 4.4 Deploy Application

```bash
# On EC2 instance

# Clone repository
git clone https://github.com/yourusername/duitsedar.git
cd duitsedar

# Create production environment file
cat > .env.prod << EOF
DATABASE_URL=jdbc:postgresql://your-rds-endpoint:5432/duitsedar
DB_USER=postgres
DB_PASSWORD=your-password
CLAUDE_API_KEY=your-claude-key
CLERK_SECRET_KEY=your-clerk-key
CLERK_PUBLISHABLE_KEY=your-clerk-pub-key
EOF

# Build and start
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Check logs
docker logs -f duitsedar-app
```

### 4.5 Security Group Configuration

```
Inbound Rules:
- SSH (22) from Your IP
- HTTP (80) from Anywhere
- HTTPS (443) from Anywhere

Outbound Rules:
- All traffic to Anywhere

RDS Security Group:
- PostgreSQL (5432) from EC2 Security Group only
```

---

## 5. Environment Variables

### 5.1 Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `jdbc:postgresql://localhost:5432/duitsedar` |
| `DB_USER` | Database username | `postgres` |
| `DB_PASSWORD` | Database password | `secure-password` |
| `CLAUDE_API_KEY` | Anthropic API key | `sk-ant-...` |
| `CLERK_SECRET_KEY` | Clerk backend secret | `sk_live_...` |
| `CLERK_PUBLISHABLE_KEY` | Clerk frontend key | `pk_live_...` |

### 5.2 Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SPRING_PROFILES_ACTIVE` | Spring profile | `dev` |
| `SERVER_PORT` | Application port | `8080` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `SENTRY_DSN` | Sentry error tracking | - |

### 5.3 Environment File Template

```bash
# .env.example

# Database
DATABASE_URL=jdbc:postgresql://localhost:5432/duitsedar
DB_USER=postgres
DB_PASSWORD=postgres

# Claude AI
CLAUDE_API_KEY=sk-ant-your-key-here

# Clerk Authentication
CLERK_SECRET_KEY=sk_test_your-key-here
CLERK_PUBLISHABLE_KEY=pk_test_your-key-here

# Optional: Monitoring
SENTRY_DSN=
PLAUSIBLE_DOMAIN=

# Spring
SPRING_PROFILES_ACTIVE=dev
```

---

## 6. CI/CD Pipeline

### 6.1 GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy DuitSedar

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      
      - name: Run tests
        working-directory: ./backend
        run: ./gradlew test
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Run frontend tests
        working-directory: ./frontend
        run: |
          npm ci
          npm test

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to EC2
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ec2-user
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            cd /home/ec2-user/duitsedar
            git pull origin main
            docker-compose -f docker-compose.prod.yml pull
            docker-compose -f docker-compose.prod.yml up -d
            docker system prune -f
```

---

## 7. Monitoring & Logging

### 7.1 Sentry Integration

```java
// Add to build.gradle
implementation 'io.sentry:sentry-spring-boot-starter:6.+'

// application.yml
sentry:
  dsn: ${SENTRY_DSN:}
  traces-sample-rate: 1.0
  environment: ${SPRING_PROFILES_ACTIVE:dev}
```

### 7.2 Health Check Endpoint

```java
// Already included via Spring Boot Actuator
// GET /actuator/health

{
  "status": "UP",
  "components": {
    "db": {"status": "UP"},
    "diskSpace": {"status": "UP"}
  }
}
```

### 7.3 Log Configuration

```yaml
# application.yml
logging:
  level:
    root: INFO
    com.duitsedar: DEBUG
    org.springframework.web: INFO
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} - %msg%n"
  file:
    name: logs/duitsedar.log
    max-size: 10MB
    max-history: 7
```

---

## 8. Troubleshooting

### 8.1 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Database connection refused | RDS security group | Add EC2 security group to RDS inbound rules |
| Out of memory | t3.micro limit | Add swap space or upgrade instance |
| Claude API errors | Rate limit or invalid key | Check key, implement retry logic |
| Clerk auth fails | Invalid keys | Verify keys match environment |

### 8.2 Debug Commands

```bash
# Check container logs
docker logs -f duitsedar-app

# Check database connection
docker exec duitsedar-app curl -s localhost:8080/actuator/health

# Check disk space
df -h

# Check memory
free -m

# Check running containers
docker ps -a

# Restart application
docker-compose -f docker-compose.prod.yml restart
```

### 8.3 Database Troubleshooting

```bash
# Connect to RDS from EC2
psql -h your-rds-endpoint -U postgres -d duitsedar

# Check table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

# Check active connections
SELECT count(*) FROM pg_stat_activity;

# Check slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

---

**Document End**

*Next Document: 09_CLAUDE_CODE_PROMPTS.md*
