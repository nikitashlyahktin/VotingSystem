import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.app.infrastructure.database.database import get_db_session, get_db


class TestDatabaseConnection:
    """Tests for database session handling"""
    
    @pytest.mark.asyncio
    async def test_get_db(self):
        """Test the get_db generator function"""
        # Create a mock database session
        mock_session = AsyncMock()
        mock_session.close = AsyncMock()
        
        # Create a mock session maker that returns our mock session
        mock_session_maker = MagicMock(return_value=mock_session)
        
        # Use patch to replace AsyncSessionLocal with our mock
        with patch('backend.app.infrastructure.database.database.AsyncSessionLocal', 
                   return_value=mock_session_maker):
            # Get the generator
            db_generator = get_db()
            
            # Get the first value from the generator (normally handled by dependency injection)
            db = await anext(db_generator)
            
            # Verify it's our mock session
            assert db == mock_session
            
            # Complete generator (like FastAPI would do after request)
            try:
                await anext(db_generator)
            except StopAsyncIteration:
                pass
            
            # Verify close was called
            mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_db_session(self):
        """Test the get_db_session synchronous function for SQLAlchemy ORM"""
        # Create a mock session
        mock_session = MagicMock()
        mock_session.close = MagicMock()
        
        # Mock the session maker
        with patch('backend.app.infrastructure.database.database.SessionLocal', 
                   return_value=mock_session):
            # Get the generator
            db_generator = get_db_session()
            
            # Get the value (normally handled by dependency injection)
            db = next(db_generator)
            
            # Verify it's our mock session
            assert db == mock_session
            
            # Complete generator (like FastAPI would do after request)
            try:
                next(db_generator)
            except StopIteration:
                pass
            
            # Verify close was called
            mock_session.close.assert_called_once() 