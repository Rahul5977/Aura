from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    firstName: Optional[str] = None
    lastName: Optional[str] = None

class UserCreate(UserBase):
    password: str
    confirmPassword: str
    
    @validator('email')
    def validate_email_domain(cls, v):
        """Validate email belongs to allowed domain"""
        if not v.endswith('@iitbhilai.ac.in'):
            raise ValueError('Only @iitbhilai.ac.in domain emails are allowed')
        return v
    
    @validator('confirmPassword')
    def passwords_match(cls, v, values):
        """Validate that passwords match"""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str
    isActive: bool
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True

class UserInDB(UserResponse):
    hashedPassword: str

# Token Schemas
class Token(BaseModel):
    accessToken: str
    tokenType: str = "bearer"
    expiresIn: int

class TokenData(BaseModel):
    email: Optional[str] = None

# Conversation Schemas
class ConversationBase(BaseModel):
    title: Optional[str] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationResponse(ConversationBase):
    id: str
    userId: str
    createdAt: datetime
    updatedAt: datetime
    
    class Config:
        from_attributes = True

# Message Schemas
class MessageBase(BaseModel):
    content: str
    role: str  # 'user', 'assistant', 'system'

class MessageCreate(MessageBase):
    conversationId: str

class MessageResponse(MessageBase):
    id: str
    conversationId: str
    userId: str
    createdAt: datetime
    
    class Config:
        from_attributes = True

# Response Schemas
class StandardResponse(BaseModel):
    message: str
    success: bool = True

class ErrorResponse(BaseModel):
    detail: str
    success: bool = False