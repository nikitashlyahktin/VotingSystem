# SQR Project Voting System

A secure and scalable voting system built with FastAPI and Streamlit.

## Features

- User registration and authentication with JWT tokens
- Create polls with single or multiple choice options
- Set automatic closing dates for polls
- Vote in active polls
- View poll results in real-time
- Modern and responsive UI with Streamlit
- Secure password hashing with bcrypt
- SQLite database for data persistence

## Requirements

- Python 3.11 or higher
- Poetry for dependency management

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/voting-system.git
cd voting-system
```

2. Install dependencies using Poetry:
```bash
poetry install
```

## Running the Application

1. Start the FastAPI backend:
```bash
cd backend
poetry run uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000
API documentation is available at http://localhost:8000/docs

2. Start the Streamlit frontend (in a new terminal):
```bash
cd frontend
poetry run streamlit run app.py
```

The frontend will be available at http://localhost:8501

## Project Structure

```
voting-system/
├── backend/
│   ├── app/
│   │   ├── application/
│   │   │   └── routers/
│   │   ├── domain/
│   │   │   └── schemas.py
│   │   ├── infrastructure/
│   │   │   ├── database/
│   │   │   └── security/
│   │   └── main.py
│   └── tests/
├── frontend/
│   └── app.py
├── poetry.lock
└── pyproject.toml
```

## Testing

Run the test suite:
```bash
poetry run pytest
```

## Security Features

- Password hashing using bcrypt
- JWT token-based authentication
- SQL injection protection with SQLAlchemy
- XSS protection
- Input validation with Pydantic
- CORS configuration
- Rate limiting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
 