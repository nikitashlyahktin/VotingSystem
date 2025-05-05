# Voting System

A full-stack web application for creating and managing polls, built with FastAPI (backend) and Streamlit (frontend).

## Features

- User Authentication
  - Registration with email and username
  - Login with email and password
  - JWT-based authentication
  - Protected routes

- Poll Management
  - Create polls with multiple options
  - Set poll closing dates
  - Allow single or multiple choice voting
  - View poll results with vote counts and percentages
  - Close polls manually

- Voting System
  - Vote on active polls
  - Change votes before poll closes
  - View real-time results
  - Visual representation of voting percentages

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- SQLite
- Poetry for dependency management
- JWT for authentication

### Frontend
- Streamlit
- Requests for API communication

## Project Structure

```
VotingSystem/
├── backend/
│   ├── app/
│   │   ├── application/
│   │   │   ├── dtos/
│   │   │   ├── routers/
│   │   │   └── use_cases/
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   │   ├── database/
│   │   │   └── security/
│   │   └── main.py
│   ├── run.py
│   └── test_server.py
├── frontend/
│   └── app.py
├── poetry.lock
├── pyproject.toml
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.10+
- Poetry

### Installation

1. Clone the repository:
```bash
git clone git@github.com:nikitashlyahktin/VotingSystem.git
cd VotingSystem
```

2. Install dependencies:
```bash
poetry install
```

3. Start the backend server:
```bash
cd backend
poetry run python run.py
```

4. Start the frontend server:
```bash
cd frontend
poetry run python app.py
```

5. Access the application:
- Frontend: http://localhost:8501
- API Documentation: http://localhost:8000/docs

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token

### Polls
- `GET /polls/` - List all polls
- `POST /polls/` - Create a new poll
- `GET /polls/{poll_id}` - Get poll details
- `POST /polls/{poll_id}/vote` - Vote on a poll
- `GET /polls/{poll_id}/results` - Get poll results
- `POST /polls/{poll_id}/close` - Close a poll

### Users
- `GET /users/me` - Get current user information

## Development

### Backend
The backend is built with FastAPI and follows a clean architecture pattern:
- Domain layer: Business logic and entities
- Application layer: Use cases and DTOs
- Infrastructure layer: Database and security implementations

### Frontend
The frontend is built with Streamlit and provides a simple, intuitive interface for:
- User authentication
- Poll creation and management
- Voting on polls
- Viewing results

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
 