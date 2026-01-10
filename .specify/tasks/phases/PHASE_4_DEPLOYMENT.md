# Phase 4: Deployment

> AWS deployment with CI/CD pipeline

**Target**: Week 7-8
**Status**: Not Started
**Tasks**: 8
**Depends On**: Phase 3

---

## Objectives

1. Containerize application
2. Set up local development environment
3. Deploy infrastructure to AWS
4. Configure database and caching
5. Implement CI/CD pipeline
6. Set up monitoring and alerting

---

## Task Breakdown

### D-001: Docker Containerization

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: U-010

Create Dockerfiles for all services:

**Backend Dockerfile**:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile**:
```dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

**Acceptance Criteria**:
- [ ] Backend Dockerfile builds successfully
- [ ] Frontend Dockerfile builds successfully
- [ ] Images run locally
- [ ] Environment variables configurable
- [ ] Multi-stage builds for small images

---

### D-002: Docker Compose (Local Dev)

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: D-001

Local development environment:

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://redis:6379
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=ringgitsense
      - POSTGRES_PASSWORD=local_dev_password
      - POSTGRES_DB=ringgitsense
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

**Acceptance Criteria**:
- [ ] `docker-compose up` starts all services
- [ ] Backend connects to DB and Redis
- [ ] Frontend connects to backend
- [ ] Hot reload for development
- [ ] Volume persistence for DB

---

### D-003: AWS Infrastructure

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: D-001

Set up AWS resources (Terraform or CDK):

**Resources**:
- VPC with public/private subnets
- ECS Fargate cluster
- Application Load Balancer
- RDS PostgreSQL instance
- ElastiCache Redis cluster
- S3 bucket for static assets
- CloudFront distribution
- ECR repositories
- Secrets Manager for API keys

**Architecture**:
```
┌─────────────────────────────────────────────────────────────┐
│                         AWS Cloud                            │
│                                                              │
│  ┌─────────────┐                    ┌─────────────────────┐ │
│  │ CloudFront  │                    │        VPC          │ │
│  │    CDN      │                    │                     │ │
│  └──────┬──────┘                    │  ┌───────────────┐  │ │
│         │                           │  │ ECS Fargate   │  │ │
│         │                           │  │ (Backend)     │  │ │
│         │                           │  └───────────────┘  │ │
│         │       ┌───────────────────┤                     │ │
│         │       │                   │  ┌───────────────┐  │ │
│         ▼       ▼                   │  │ RDS           │  │ │
│  ┌─────────────────┐               │  │ (PostgreSQL)  │  │ │
│  │      ALB        │               │  └───────────────┘  │ │
│  └─────────────────┘               │                     │ │
│                                     │  ┌───────────────┐  │ │
│  ┌─────────────────┐               │  │ ElastiCache   │  │ │
│  │       S3        │               │  │ (Redis)       │  │ │
│  │ (Static Assets) │               │  └───────────────┘  │ │
│  └─────────────────┘               └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Acceptance Criteria**:
- [ ] VPC created with proper subnets
- [ ] ECS cluster configured
- [ ] ALB set up
- [ ] Security groups configured
- [ ] IAM roles created
- [ ] Infrastructure as code committed

---

### D-004: RDS PostgreSQL Setup

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: D-003

Configure production database:

**Specifications**:
- Instance: db.t3.small (start small)
- Storage: 20GB GP3
- Multi-AZ: No (cost saving for MVP)
- Backup: 7 days retention
- Encryption: At rest enabled

**Tasks**:
- Create RDS instance
- Configure security groups
- Set up connection secrets
- Run migrations
- Test connection from ECS

**Acceptance Criteria**:
- [ ] RDS instance running
- [ ] Accessible from ECS tasks
- [ ] Migrations applied
- [ ] Backups configured
- [ ] Connection string in Secrets Manager

---

### D-005: ECS Fargate Deployment

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: D-003

Deploy backend to ECS Fargate:

**Configuration**:
- Task Definition: 0.5 vCPU, 1GB RAM (start small)
- Service: 1 task (scale later)
- Health check: `/health` endpoint
- Logging: CloudWatch Logs

**Tasks**:
- Create ECR repository
- Push Docker image
- Create task definition
- Create ECS service
- Configure auto-scaling (optional)

**Acceptance Criteria**:
- [ ] ECR repository created
- [ ] Image pushed successfully
- [ ] Task definition created
- [ ] Service running
- [ ] Health checks passing
- [ ] Logs visible in CloudWatch

---

### D-006: GitHub Actions CI/CD

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: D-005

Automated deployment pipeline:

**Workflows**:

1. **CI (Pull Request)**:
   - Run linting
   - Run tests
   - Build Docker images
   - Comment test coverage

2. **CD (Push to main)**:
   - Build Docker images
   - Push to ECR
   - Deploy to ECS
   - Run smoke tests

**CI Workflow** (`.github/workflows/ci.yml`):
```yaml
name: CI
on:
  pull_request:
    branches: [main, develop]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov
```

**Acceptance Criteria**:
- [ ] CI runs on PRs
- [ ] Tests must pass to merge
- [ ] CD deploys on push to main
- [ ] Rollback capability
- [ ] Secrets stored securely

---

### D-007: SSL/TLS and Domain Setup

**Priority**: High | **Status**: ⬜ Not Started | **Depends On**: D-005

Configure HTTPS and custom domain:

**Tasks**:
- Register/configure domain (if needed)
- Create ACM certificate
- Configure CloudFront with certificate
- Set up Route 53 DNS records
- Redirect HTTP to HTTPS

**Acceptance Criteria**:
- [ ] Domain configured
- [ ] SSL certificate issued
- [ ] HTTPS working
- [ ] HTTP redirects to HTTPS
- [ ] CloudFront serving frontend

---

### D-008: Monitoring and Alerting

**Priority**: Medium | **Status**: ⬜ Not Started | **Depends On**: D-005

Set up observability:

**CloudWatch**:
- Application logs
- Error rate alarms
- Latency alarms
- Cost alarms

**Dashboards**:
- Request count
- Error rate
- Response time (p50, p95)
- Database connections
- Cache hit rate

**Alerts**:
- Error rate > 5% → Slack/Email
- Latency p95 > 3s → Slack/Email
- Database CPU > 80% → Email
- Monthly cost > budget → Email

**Acceptance Criteria**:
- [ ] CloudWatch logs configured
- [ ] Alarms created
- [ ] Dashboard set up
- [ ] Alert notifications working
- [ ] Runbook for common issues

---

## Exit Criteria

Phase 4 is complete when:

1. ✅ Application running on AWS
2. ✅ CI/CD pipeline functional
3. ✅ HTTPS with custom domain
4. ✅ Monitoring and alerting active
5. ✅ All D-xxx tasks marked Done

---

## Production Checklist

Before go-live:

- [ ] All environment variables set
- [ ] API keys rotated from dev
- [ ] Database backups verified
- [ ] SSL certificate valid
- [ ] Health checks passing
- [ ] Monitoring alarms configured
- [ ] Error tracking enabled
- [ ] Load testing completed
- [ ] Security scan passed
- [ ] PDPA compliance verified

---

## Dependencies

| External | Internal |
|----------|----------|
| AWS Account | Phase 3 complete |
| Domain name (optional) | D-003 |
| Anthropic API key | D-005 |

---

## Cost Estimation (MVP)

| Service | Monthly Cost |
|---------|-------------|
| ECS Fargate | ~$15-30 |
| RDS (db.t3.small) | ~$25-35 |
| ElastiCache | ~$15-25 |
| ALB | ~$20 |
| CloudFront | ~$5-10 |
| S3 | ~$1-5 |
| **Total** | **~$80-130/month** |

*Note: Costs vary by usage. Enable billing alerts.*

---

**Document Status**: Complete
**Last Updated**: 2026-01-10
