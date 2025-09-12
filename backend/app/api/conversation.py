from fastapi import APIRouter, Depends, HTTPException, status
from prisma import Prisma
from typing import List

from app.db.schemas import (
    ConversationCreate, ConversationResponse, 
    MessageCreate, MessageResponse, UserResponse
)
from app.db.sessions import get_database
from app.api.auth import get_current_user

# Create router instance
router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Prisma = Depends(get_database)
):
    """
    Create a new conversation.
    
    This is a protected endpoint that creates a new conversation
    for the authenticated user.
    
    Args:
        conversation_data: Conversation creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created conversation
    """
    conversation = await db.conversation.create(
        data={
            "title": conversation_data.title,
            "userId": current_user.id,
        }
    )
    
    return ConversationResponse.model_validate(conversation)

@router.get("/", response_model=List[ConversationResponse])
async def get_user_conversations(
    current_user: UserResponse = Depends(get_current_user),
    db: Prisma = Depends(get_database)
):
    """
    Get all conversations for the current user.
    
    This is a protected endpoint that returns all conversations
    belonging to the authenticated user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of user's conversations
    """
    conversations = await db.conversation.find_many(
        where={"userId": current_user.id},
        order={"updatedAt": "desc"}
    )
    
    return [ConversationResponse.model_validate(conv) for conv in conversations]

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Prisma = Depends(get_database)
):
    """
    Get a specific conversation.
    
    This is a protected endpoint that returns a specific conversation
    if it belongs to the authenticated user.
    
    Args:
        conversation_id: ID of the conversation to retrieve
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Conversation details
        
    Raises:
        HTTPException: If conversation not found or doesn't belong to user
    """
    conversation = await db.conversation.find_unique(
        where={"id": conversation_id}
    )
    
    if not conversation or conversation.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    return ConversationResponse.model_validate(conversation)

@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    conversation_id: str,
    message_data: MessageCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Prisma = Depends(get_database)
):
    """
    Create a new message in a conversation.
    
    This is a protected endpoint that creates a new message
    in a conversation belonging to the authenticated user.
    
    Args:
        conversation_id: ID of the conversation
        message_data: Message creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created message
        
    Raises:
        HTTPException: If conversation not found or doesn't belong to user
    """
    # Verify conversation belongs to user
    conversation = await db.conversation.find_unique(
        where={"id": conversation_id}
    )
    
    if not conversation or conversation.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Create message
    message = await db.message.create(
        data={
            "content": message_data.content,
            "role": message_data.role,
            "conversationId": conversation_id,
            "userId": current_user.id,
        }
    )
    
    return MessageResponse.model_validate(message)

@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: Prisma = Depends(get_database)
):
    """
    Get all messages in a conversation.
    
    This is a protected endpoint that returns all messages
    in a conversation belonging to the authenticated user.
    
    Args:
        conversation_id: ID of the conversation
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List of messages in the conversation
        
    Raises:
        HTTPException: If conversation not found or doesn't belong to user
    """
    # Verify conversation belongs to user
    conversation = await db.conversation.find_unique(
        where={"id": conversation_id}
    )
    
    if not conversation or conversation.userId != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get messages
    messages = await db.message.find_many(
        where={"conversationId": conversation_id},
        order={"createdAt": "asc"}
    )
    
    return [MessageResponse.model_validate(msg) for msg in messages]