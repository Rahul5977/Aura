import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from prisma import Prisma

from app.main import app
from app.db.sessions import prisma
from app.core.security import get_password_hash

# Test configuration
TEST_EMAIL = "test@iitbhilai.ac.in"
TEST_PASSWORD = "TestPass123"
TEST_USER_DATA = {
    "email": TEST_EMAIL,
    "password": TEST_PASSWORD,
    "confirmPassword": TEST_PASSWORD,
    "firstName": "Test",
    "lastName": "User"
}

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def setup_database():
    """Setup test database."""
    await prisma.connect()
    yield
    await prisma.disconnect()

@pytest.fixture
async def clean_database():
    """Clean database before each test."""
    # Delete all test data
    await prisma.message.delete_many()
    await prisma.conversation.delete_many()
    await prisma.user.delete_many()
    yield

@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)

@pytest.fixture
async def async_client():
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def test_user():
    """Create a test user in the database."""
    user = await prisma.user.create(
        data={
            "email": TEST_EMAIL,
            "hashedPassword": get_password_hash(TEST_PASSWORD),
            "firstName": "Test",
            "lastName": "User",
        }
    )
    return user

class TestAuthentication:
    """Test suite for authentication endpoints."""
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, async_client: AsyncClient, clean_database):
        """Test successful user registration."""
        response = await async_client.post("/api/auth/register", json=TEST_USER_DATA)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "registered successfully" in data["message"]
    
    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, async_client: AsyncClient, test_user, clean_database):
        """Test registration with duplicate email."""
        response = await async_client.post("/api/auth/register", json=TEST_USER_DATA)
        
        assert response.status_code == 400
        data = response.json()
        assert "Email already registered" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_register_invalid_domain(self, async_client: AsyncClient, clean_database):
        """Test registration with invalid email domain."""
        invalid_user_data = TEST_USER_DATA.copy()
        invalid_user_data["email"] = "test@gmail.com"
        
        response = await async_client.post("/api/auth/register", json=invalid_user_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "domain emails are allowed" in str(data)
    
    @pytest.mark.asyncio
    async def test_login_success(self, async_client: AsyncClient, test_user, clean_database):
        """Test successful login."""
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        response = await async_client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "accessToken" in data
        assert data["tokenType"] == "bearer"
        assert "expiresIn" in data
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, async_client: AsyncClient, test_user, clean_database):
        """Test login with invalid credentials."""
        login_data = {
            "email": TEST_EMAIL,
            "password": "wrongpassword"
        }
        response = await async_client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "Incorrect email or password" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_get_current_user(self, async_client: AsyncClient, test_user, clean_database):
        """Test getting current user information."""
        # First login to get token
        login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
        login_response = await async_client.post("/api/auth/login", json=login_data)
        token = login_response.json()["accessToken"]
        
        # Use token to get user info
        headers = {"Authorization": f"Bearer {token}"}
        response = await async_client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_EMAIL
        assert data["firstName"] == "Test"
        assert data["lastName"] == "User"
    
    @pytest.mark.asyncio
    async def test_protected_route_without_token(self, async_client: AsyncClient):
        """Test accessing protected route without token."""
        response = await async_client.get("/api/auth/me")
        
        assert response.status_code == 403

class TestConversations:
    """Test suite for conversation endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_conversation(self, async_client: AsyncClient, test_user, clean_database):
        """Test creating a conversation."""
        # Login to get token
        login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
        login_response = await async_client.post("/api/auth/login", json=login_data)
        token = login_response.json()["accessToken"]
        
        # Create conversation
        headers = {"Authorization": f"Bearer {token}"}
        conversation_data = {"title": "Test Conversation"}
        response = await async_client.post("/api/conversations/", json=conversation_data, headers=headers)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Conversation"
        assert data["userId"] == test_user.id
    
    @pytest.mark.asyncio
    async def test_get_conversations(self, async_client: AsyncClient, test_user, clean_database):
        """Test getting user conversations."""
        # Login to get token
        login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
        login_response = await async_client.post("/api/auth/login", json=login_data)
        token = login_response.json()["accessToken"]
        
        # Create a conversation first
        headers = {"Authorization": f"Bearer {token}"}
        conversation_data = {"title": "Test Conversation"}
        await async_client.post("/api/conversations/", json=conversation_data, headers=headers)
        
        # Get conversations
        response = await async_client.get("/api/conversations/", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Conversation"

class TestSecurity:
    """Test suite for security features."""
    
    @pytest.mark.asyncio
    async def test_password_strength_validation(self, async_client: AsyncClient, clean_database):
        """Test password strength validation."""
        weak_password_data = TEST_USER_DATA.copy()
        weak_password_data["password"] = "weak"
        weak_password_data["confirmPassword"] = "weak"
        
        response = await async_client.post("/api/auth/register", json=weak_password_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "at least 8 characters" in str(data)
    
    @pytest.mark.asyncio
    async def test_password_mismatch(self, async_client: AsyncClient, clean_database):
        """Test password confirmation mismatch."""
        mismatch_data = TEST_USER_DATA.copy()
        mismatch_data["confirmPassword"] = "DifferentPassword123"
        
        response = await async_client.post("/api/auth/register", json=mismatch_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "do not match" in str(data)
    
    @pytest.mark.asyncio
    async def test_invalid_token(self, async_client: AsyncClient):
        """Test accessing protected route with invalid token."""
        headers = {"Authorization": "Bearer invalid-token"}
        response = await async_client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "Could not validate credentials" in data["detail"]
