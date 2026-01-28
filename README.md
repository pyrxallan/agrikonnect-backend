# Agrikonnect Backend

<div align="center">

[![CI/CD Pipeline](https://github.com/pyrxallan/agrikonnect-backend/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/pyrxallan/agrikonnect-backend/actions)
[![Python Version](https://img.shields.io/badge/python-3.9+-166534?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3+-166534?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-14+-4ade80?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/docker-ready-4ade80?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-facc15)](LICENSE)

**The RESTful API powering Agrikonnect - where agricultural knowledge meets community**

[Features](#features) • [Quick Start](#getting-started) • [API Docs](#api-documentation) • [Contributing](#contributing)

</div>

---

The backend API for Agrikonnect, a centralized agricultural knowledge-sharing platform connecting farmers, experts, and communities through posts, messaging, and real-time notifications.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Development Guidelines](#development-guidelines)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Team](#team)

## 🎯 Overview

Agrikonnect Backend is a RESTful API built with Flask that powers the Agricultural Super App. It provides secure authentication, content management, social networking features, real-time messaging, and administrative capabilities for managing agricultural knowledge sharing.

### Core Goals

- **Centralize Agricultural Knowledge**: Create a hub for agricultural information and best practices
- **Enable Expert-Farmer Interaction**: Facilitate direct communication between agricultural experts and farmers
- **Ensure Scalability**: Support growing user base and feature set
- **Maintain Security**: Implement robust authentication and data protection

## Features

<table>
<tr>
<td width="50%">

### User Management
- User registration and authentication
- JWT-based secure sessions with refresh tokens
- Role-based access control (Farmer, Expert, Admin)
- Profile management and customization
- Password reset functionality

### Content Management
- Create, read, update, and delete blog posts
- Image upload and storage for posts
- Like and comment on posts
- Personalized feed based on followed experts and communities

</td>
<td width="50%">

### Networking
- Follow/unfollow agricultural experts
- Join/leave agricultural communities
- Discover experts and communities

### Communication
- Direct messaging between users
- Real-time notifications via microservice
- Message history and management

### Administration
- User management and moderation
- Content moderation tools
- System analytics and monitoring

</td>
</tr>
</table>

## Architecture

> **Monolith + Microservice Architecture**

<div align="center">

```
┌────────────────────────────────────────┐
│     Flask Backend (Monolith API)       │
│  Auth • Posts • Communities • Messages │
│  JWT • Swagger • Validation            │
└──────────────┬───────────────┬─────────┘
               │               │
               ▼               ▼
┌─────────────────────┐  ┌────────────────────────┐
│   PostgreSQL DB     │  │ Notification Microservice│
│ (Docker Container)  │  │  (Independent Flask App) │
└─────────────────────┘  └────────────────────────┘
```

</div>

**Main Application Components:**
- Authentication and authorization
- Posts and content management
- Communities and social networking
- Messaging system
- User profiles

**Microservice:**
- Dedicated notification service
- Independent Flask application
- Communicates via HTTP/message queue
- Scalable and independently deployable

## Technology Stack

<div align="center">

| Category | Technology | Version |
|----------|-----------|---------|
| **Framework** | ![Flask](https://img.shields.io/badge/Flask-166534?style=flat&logo=flask&logoColor=white) | 2.3+ |
| **API Design** | ![REST](https://img.shields.io/badge/REST-4ade80?style=flat) Flask-RESTful / Flask-RESTX | - |
| **Authentication** | ![JWT](https://img.shields.io/badge/JWT-facc15?style=flat) | - |
| **Database** | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4ade80?style=flat&logo=postgresql&logoColor=white) | 14+ |
| **ORM** | ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-166534?style=flat) | - |
| **Documentation** | ![Swagger](https://img.shields.io/badge/Swagger-facc15?style=flat&logo=swagger&logoColor=black) | OpenAPI 3.0 |
| **Testing** | ![Pytest](https://img.shields.io/badge/Pytest-4ade80?style=flat&logo=pytest&logoColor=white) | - |
| **Containerization** | ![Docker](https://img.shields.io/badge/Docker-166534?style=flat&logo=docker&logoColor=white) | - |
| **CI/CD** | ![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-facc15?style=flat&logo=github-actions&logoColor=black) | - |

</div>

## Getting Started

### Prerequisites

```bash
Python 3.9+
PostgreSQL 14+
Docker & Docker Compose (optional but recommended)
Git
```

### Installation

> **Choose your preferred setup method**

<details open>
<summary><b>Option 1: Docker Setup (Recommended)</b></summary>

<br>

**Step 1:** Clone the repository
```bash
git clone https://github.com/pyrxallan/agrikonnect-backend.git
cd agrikonnect-backend
```

**Step 2:** Configure environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

**Step 3:** Build and run with Docker Compose
```bash
docker-compose up --build
```

The API will be available at `http://localhost:5000`

</details>

<details>
<summary><b>Option 2: Local Development</b></summary>

<br>

**Step 1:** Clone the repository
```bash
git clone https://github.com/pyrxallan/agrikonnect-backend.git
cd agrikonnect-backend
```

**Step 2:** Create and activate virtual environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

**Step 3:** Install dependencies
```bash
pip install -r requirements.txt
```

**Step 4:** Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

**Step 5:** Initialize the database
```bash
flask db upgrade
flask seed  # Optional: seed test data
```

**Step 6:** Run the application
```bash
flask run
```

The API will be available at `http://localhost:5000`

</details>

### Environment Variables

Create a `.env` file in the root directory:

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/agrikonnect
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/agrikonnect_test

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# CORS Configuration
CORS_ORIGINS=http://localhost:3000

# File Upload Configuration
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Notification Service
NOTIFICATION_SERVICE_URL=http://localhost:5001
```

## Project Structure

> **Clean, modular architecture for scalability and maintainability**

```
agrikonnect-backend/
├── app/
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration settings
│   ├── extensions.py            # Flask extensions
│   ├── models/                  # Database models
│   ├── routes/                  # API endpoints
│   ├── services/                # Business logic
│   ├── schemas/                 # Request/response schemas
│   ├── utils/                   # Utility functions
│   ├── auth/                    # Authentication logic
│   └── tests/                   # Test suite
├── microservices/
│   └── notifications/           # Notification microservice
│       ├── app/
│       ├── tests/
│       └── Dockerfile
├── migrations/                  # Database migrations
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Docker Compose setup
└── .github/workflows/           # CI/CD pipeline
```

## API Documentation

### Interactive Documentation

> Access comprehensive, interactive API documentation

<div align="center">

| Documentation | URL |
|--------------|-----|
| **Swagger UI** | `http://localhost:5000/api/docs` |
| **OpenAPI Spec** | `http://localhost:5000/api/swagger.json` |

</div>

### API Versioning

All API endpoints are versioned and follow the pattern:
```
/api/v1/{resource}
```

### Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```http
Authorization: Bearer <your_access_token>
```

### Key Endpoints

<details>
<summary><b>Authentication Endpoints</b></summary>

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout user
- `POST /api/v1/auth/password-reset` - Request password reset
- `PUT /api/v1/auth/password-reset/<token>` - Reset password

</details>

<details>
<summary><b>User Endpoints</b></summary>

- `GET /api/v1/users/profile` - Get current user profile
- `PUT /api/v1/users/profile` - Update user profile
- `GET /api/v1/users/<user_id>` - Get user by ID

</details>

<details>
<summary><b>Post Endpoints</b></summary>

- `GET /api/v1/posts` - Get all posts (paginated)
- `POST /api/v1/posts` - Create new post
- `GET /api/v1/posts/<post_id>` - Get post by ID
- `PUT /api/v1/posts/<post_id>` - Update post
- `DELETE /api/v1/posts/<post_id>` - Delete post
- `POST /api/v1/posts/<post_id>/like` - Like/unlike post
- `POST /api/v1/posts/<post_id>/comments` - Add comment

</details>

<details>
<summary><b>Community Endpoints</b></summary>

- `GET /api/v1/communities` - Get all communities
- `POST /api/v1/communities` - Create community
- `GET /api/v1/communities/<community_id>` - Get community details
- `POST /api/v1/communities/<community_id>/follow` - Follow/unfollow community

</details>

<details>
<summary><b>Expert Endpoints</b></summary>

- `GET /api/v1/experts` - Get all experts
- `POST /api/v1/experts/<expert_id>/follow` - Follow/unfollow expert

</details>

<details>
<summary><b>Message Endpoints</b></summary>

- `GET /api/v1/messages` - Get user messages
- `POST /api/v1/messages` - Send message
- `GET /api/v1/messages/<message_id>` - Get message details

</details>

<details>
<summary><b>Admin Endpoints</b></summary>

- `GET /api/v1/admin/users` - Get all users (admin only)
- `PUT /api/v1/admin/users/<user_id>/moderate` - Moderate user
- `DELETE /api/v1/admin/posts/<post_id>` - Delete post (admin only)

</details>

### HTTP Status Codes

| Code | Description |
|------|-------------|
| ![200](https://img.shields.io/badge/200-OK-4ade80) | Request successful |
| ![201](https://img.shields.io/badge/201-Created-4ade80) | Resource created successfully |
| ![400](https://img.shields.io/badge/400-Bad_Request-facc15) | Invalid input |
| ![401](https://img.shields.io/badge/401-Unauthorized-facc15) | Authentication required |
| ![403](https://img.shields.io/badge/403-Forbidden-facc15) | Insufficient permissions |
| ![404](https://img.shields.io/badge/404-Not_Found-facc15) | Resource not found |
| ![500](https://img.shields.io/badge/500-Server_Error-red) | Internal server error |

## Development Guidelines

### Branch Strategy

> **We follow a simplified Git Flow workflow**

```
main        ──●────────●────────●──────→  Production releases
               │        │        │
dev         ───●────●───●────●───●──────→  Integration branch
                    │        │
feature/*   ────────●────────●──────────→  Feature development
```

**Branch Types:**
- `main` - Production-ready code, protected branch
- `dev` - Integration branch for ongoing development
- `feature/<feature-name>` - Individual feature branches

### Workflow

**Step 1:** Pull latest changes from `dev`
```bash
git checkout dev
git pull origin dev
```

**Step 2:** Create feature branch
```bash
git checkout -b feature/your-feature-name
```

**Step 3:** Make changes and commit
```bash
git add .
git commit -m "feat: add your feature description"
```

**Step 4:** Push branch and create Pull Request
```bash
git push origin feature/your-feature-name
```

**Step 5:** Request review and merge into `dev`

### Commit Message Format

Follow conventional commits:

```
<type>: <description>

[optional body]
```

<table>
<tr>
<td width="50%">

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions or modifications
- `refactor:` Code refactoring

</td>
<td width="50%">

**Examples:**
```bash
feat: add post creation endpoint
fix: resolve JWT expiration bug
docs: update API documentation
test: add unit tests for user model
refactor: optimize database queries
```

</td>
</tr>
</table>

### Code Style

- Follow **PEP 8** Python style guide
- Use meaningful variable and function names
- Write docstrings for all functions and classes
- Keep functions small and focused
- Use type hints where appropriate
- Add comments for complex logic

### API Design Principles

| Principle | Description |
|-----------|-------------|
| **RESTful conventions** | Use appropriate HTTP methods (GET, POST, PUT, DELETE) |
| **Consistent naming** | Use lowercase with hyphens for endpoints |
| **Versioning** | Include version in URL path (/api/v1/) |
| **Validation** | Validate all inputs before processing |
| **Error handling** | Return meaningful error messages with proper status codes |
| **Documentation** | Document all endpoints in Swagger |

## Testing

> **Ensure code quality with comprehensive testing**

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_auth.py

# Run tests with verbose output
pytest -v
```

### Test Structure

<table>
<tr>
<td width="33%">

**Unit Tests**
- Test individual models
- Test utility functions
- Validate business logic

</td>
<td width="33%">

**Integration Tests**
- Test API endpoints
- Test database operations
- Test service interactions

</td>
<td width="33%">

**Authentication Tests**
- Test JWT generation
- Test token validation
- Test authorization logic

</td>
</tr>
</table>

### Coverage Requirements

![Coverage](https://img.shields.io/badge/coverage-80%25+-4ade80)

- Minimum **80% code coverage**
- All critical paths must be tested
- Tests must pass before merging

## Deployment

> **Production-ready deployment strategies**

### Supported Platforms

<div align="center">

| Platform | Status | Documentation |
|----------|--------|---------------|
| ![Heroku](https://img.shields.io/badge/Heroku-166534?logo=heroku&logoColor=white) | Supported | [Guide](#heroku) |
| ![AWS](https://img.shields.io/badge/AWS-4ade80?logo=amazon-aws&logoColor=white) | Supported | [Guide](#aws) |
| ![DigitalOcean](https://img.shields.io/badge/DigitalOcean-166534?logo=digitalocean&logoColor=white) | Supported | [Guide](#digitalocean) |

</div>

### Heroku

```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
heroku run flask db upgrade
```

### AWS / DigitalOcean

- Use Docker containers for deployment
- Configure environment variables in platform settings
- Set up PostgreSQL database instance
- Configure reverse proxy (Nginx) for production
- Enable HTTPS with SSL certificates

### Database Migrations

```bash
# Create new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

### Environment Configuration

<table>
<tr>
<td width="33%">

**Development**
- `.env` file
- Debug mode enabled
- Detailed error messages

</td>
<td width="33%">

**Staging**
- Separate environment
- Test data
- Performance monitoring

</td>
<td width="33%">

**Production**
- Secure configuration
- Production database
- Error tracking enabled

</td>
</tr>
</table>

## Contributing

> **Collaborative development with clear ownership**

### Feature Ownership Model

Each feature has a designated owner responsible for:

- ✓ Backend implementation
- ✓ Frontend integration
- ✓ Writing comprehensive tests
- ✓ API documentation
- ✓ Code review participation

### Team Responsibilities

<details open>
<summary><b>Ken - Authentication & User Profiles</b></summary>

<br>

**Backend:**
- User model and roles implementation
- JWT authentication and refresh tokens
- Password reset functionality
- Profile management APIs
- Authentication-related tests

**Frontend:**
- Login and registration pages
- Profile page (view/edit)
- Auth state management in Redux
- Protected route implementation

</details>

<details>
<summary><b>Samuel - Posts, Blogs & Media</b></summary>

<br>

**Backend:**
- Post and Comment models
- CRUD APIs for posts
- Image upload handling
- Like and comment endpoints
- Post validation and tests

**Frontend:**
- Post creation UI
- Feed UI
- Like/comment interactions
- Image rendering

</details>

<details>
<summary><b>Hillary - Experts, Communities & Following</b></summary>

<br>

**Backend:**
- Expert and Community models
- Follow/unfollow APIs
- Feed filtering logic
- Community management endpoints

**Frontend:**
- Experts and communities pages
- Follow/unfollow UI
- Personalized feed display

</details>

<details>
<summary><b>Team Member 4 - Messaging, Notifications & Admin</b></summary>

<br>

**Backend:**
- Messaging models and APIs
- Notification microservice development
- Admin moderation endpoints
- Real-time notification system

**Frontend:**
- Messaging inbox UI
- Chat window component
- Notifications UI
- Admin dashboard

</details>

### Pull Request Process

```
1. Ensure all tests pass ✓
2. Update documentation if needed ✓
3. Request review from feature owner ✓
4. Address review comments ✓
5. Merge after approval ✓
```

### Code Review Checklist

- [ ] Code follows PEP 8 style guidelines
- [ ] Tests are included and passing
- [ ] API endpoints are documented in Swagger
- [ ] Error handling is properly implemented
- [ ] Security best practices followed
- [ ] Database migrations included (if applicable)
- [ ] No sensitive data in commits

## Support

**Need help?** Here's how to get assistance:

1. Check existing [GitHub Issues](https://github.com/pyrxallan/agrikonnect-backend/issues)
2. Review the [API Documentation](#api-documentation)
3. Contact your team lead
4. Create a [new issue](https://github.com/pyrxallan/agrikonnect-backend/issues/new) with detailed description

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with dedication by the Agrikonnect Team**

[Backend Repository](https://github.com/pyrxallan/agrikonnect-backend) • [Frontend Repository](https://github.com/pyrxallan/agrikonnect-frontend)

![Agricultural Green](https://img.shields.io/badge/Theme-Agricultural_Green-166534?style=for-the-badge)

</div>
