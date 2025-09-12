
Phase 1: Foundation & Backend Architecture (Weeks 1-3)
This phase focuses on building a rock-solid, scalable backend foundation before any complex AI is introduced.
Week 1: Project Setup & Containerization
Goal: Create a reproducible development environment for the entire project.
Key Tasks:
Initialize a Git repository and define your branching strategy (e.g., GitFlow).
Set up the top-level project structure with aura-backend, aura-frontend, and ml_scripts directories.
Create the docker-compose.yml file to define the services: backend, frontend, and a PostgreSQL database.=
Build a basic Dockerfile for the FastAPI backend.
Initialize the FastAPI application and create a simple /health endpoint to test that the server runs correctly.
Tech Focus: Git, Docker, Docker Compose, FastAPI.
Milestone: You can run docker-compose up and access the /health endpoint from your browser.
Week 2: User Authentication & Database
Goal: Implement a secure system for managing users and their data.
Key Tasks:
Finalize the database schema using SQLAlchemy models for users, conversations, and messages.
Implement the user registration and login logic using JWT for token-based authentication.
Create secure API endpoints that require a valid token for access.
Write unit tests for the authentication logic.
Tech Focus: PostgreSQL, SQLAlchemy, FastAPI (Dependencies), passlib (for hashing).
Milestone: A user can register, log in to receive a JWT, and use that token to access a protected API route.
Week 3: Real-time Communication & Chat Logic
Goal: Establish a live, stateful communication channel between the server and clients.
Key Tasks:
Implement a WebSocket endpoint in FastAPI that can handle multiple client connections for a single conversation.
Develop the backend logic to receive messages via WebSocket, store them in the database (linking them to the correct user and conversation), and broadcast them to other clients in the same session.
Handle connection and disconnection events gracefully.
Tech Focus: FastAPI WebSocket.
Milestone: A basic text-based chat application can be tested using a simple Python client or a tool like Postman, demonstrating real-time message exchange.

Phase 2: Core AI/ML Integration & Prototyping (Weeks 4-7)
This phase focuses on integrating the first layer of AI models to begin processing and understanding user input.
Week 4: Multi-Modal Input Processing (Audio)
Goal: Enable the backend to understand the user's spoken words and vocal tone.
Key Tasks:
Create an endpoint to handle audio data sent over the WebSocket.
Integrate a pre-trained Speech-to-Text model (like Whisper) to transcribe the audio.
Integrate a pre-trained Speech Emotion Recognition (SER) model to analyze the vocal tone.
Tech Focus: Hugging Face transformers, librosa (for audio processing).
https://github.com/HoseinAzad/Transformer-based-SER?tab=readme-ov-file 
Speech Emotion Recognition By Fine-Tuning Wav2Vec 2.0
Milestone: The backend can receive an audio stream and return a JSON object containing the transcribed text and the detected emotion.
Week 5: Initial Contextual Analysis
Goal: Extract deeper meaning from the transcribed text.
Key Tasks:
Integrate
 COMET to infer commonsense emotional effects, a key part of modeling emotional dynamics
Integrate a pre-trained Named Entity Recognition (NER) model (e.g., from spaCy) to identify key people, places, and concepts in the conversation.
Start building the service for the Dynamic Knowledge Graph.
Tech Focus: spacy, transformers.
Milestone: The backend can take text and enrich it with a structured list of entities and commonsense inferences.
Week 6: Custom Model Data Preparation
Goal: Prepare the specialized datasets required for training your custom models.
Key Tasks:
Write and execute data cleaning and preprocessing scripts for the ESConv and ECF datasets.
Train a baseline Strategy Predictor model (e.g., using XGBoost) on the ESConv data.
Version your processed datasets (e.g., using DVC or just clear naming conventions) so your experiments are reproducible.
Tech Focus: pandas, scikit-learn.
Milestone: Clean, versioned datasets are stored and ready for the main training phase.
Week 7: Backend AI Orchestration
Goal: Create the central logic that connects all the AI services integrated so far.
Key Tasks:
Design and implement the chat_orchestrator service in FastAPI.
This service will sequentially call the STT, SER, COMET, and NER models.
The service will aggregate all the outputs into a single, structured "analysis packet."
Tech Focus: Python, FastAPI (Dependency Injection).
Milestone: A single function call can trigger the entire analysis pipeline and produce a comprehensive JSON object, ready to be used for response generation.

Phase 3: Advanced AI Development & Fine-Tuning (Weeks 8-11)
This is the most research-intensive phase, focusing on implementing the advanced multi-modal pipelines and fine-tuning the core generative model.
Week 8: Advanced Video Feature Extraction
Goal: Implement the complete video analysis pipeline as detailed in the Samsung paper.
Key Tasks:
Integrate
 LLaVA to generate text descriptions from video frames
Implement the face analysis pipeline: use
 MTCNN for face detection, MobileFaceNets for speaker identification, and a pre-trained VGG19 for facial emotion feature extraction
Tech Focus: opencv-python, torchvision, Pillow.
Milestone: The backend can process a video stream to extract facial emotion features and descriptive captions.
Week 9: Custom Model Fine-Tuning (ECE)
Goal: Train the highly specialized model for identifying the root cause of emotions.
Key Tasks:
Implement and fine-tune the two-stage Emotion Cause Extraction (ECE) module based on the methods in the Samsung paper5.
Begin generating the "Hyper-Contextual Prompt" dataset by running your processed data through the full analysis pipeline.
Tech Focus: PyTorch, Hugging Face Trainer.
Milestone: A trained ECE model is saved and benchmarked.
Week 10: GenAI Fine-Tuning (LLM)
Goal: Train the main "writer" AI to generate empathetic, context-aware responses.
Key Tasks:
Finalize the "Hyper-Contextual Prompt" dataset.
Run the LoRA fine-tuning script on a powerful base LLM (e.g., Llama 3 8B).
Tech Focus: peft, bitsandbytes, accelerate.
Milestone: A specialized, fine-tuned LLM for emotional support is created and saved.
Week 11: Final AI Integration & Memory System
Goal: Assemble the complete AI "brain" and give it long-term memory.
Key Tasks:
Integrate the newly trained ECE and fine-tuned LLM into the chat_orchestrator.
Implement the Persistent Memory service, which uses the LLM to summarize conversations and stores/retrieves them from the database.
Tech Focus: Python, SQLAlchemy.
Milestone: The backend is now fully feature-complete, capable of advanced analysis, long-term memory, and generating context-aware responses.

Phase 4: Frontend Development (Weeks 12-14)
This phase focuses on building the user-facing application.
Week 12: UI Foundation & Real-time Connection
Goal: Create a functional chat interface connected to the backend.
Key Tasks:
Set up the React project (using Vite) with state management.
Build the core chat UI components (e.g., ChatWindow, MessageBubble).
Implement the WebSocket client to establish a real-time connection with the backend.
Tech Focus: React, socket.io-client, CSS.
Milestone: A user can type a message in the browser, send it to the backend, and receive a (placeholder) response in real-time.
Week 13: Advanced UI Features
Goal: Implement multi-modal input and the explainability dashboard.
Key Tasks:
Use the MediaRecorder Web API to capture audio and video from the user and stream it over the WebSocket.
Build the UI components for the XAI (Explainable AI) dashboard to display the reasoning (cause, emotion, strategy) sent from the backend.
Tech Focus: Web APIs, React.
Milestone: A user can speak to the application, and the XAI dashboard displays the analysis results from the backend.
Week 14: Visualization & Polish
Goal: Create a polished, professional, and intuitive user experience.
Key Tasks:
Integrate a graph visualization library (e.g., react-force-graph) to display the Dynamic Knowledge Graph.
Add loading indicators, error messages, and refine the application's overall styling and responsiveness.
Tech Focus: UI/UX design, CSS.
Milestone: The frontend is fully feature-complete and provides a smooth user experience.

Phase 5: Finalization & Deployment (Weeks 15-16)
The final phase is for testing, deploying, and documenting your work.
Week 15: End-to-End Testing & Deployment
Goal: Ensure the application is stable and deploy it to a live server.
Key Tasks:
Conduct rigorous end-to-end testing of the entire workflow, from multi-modal input on the frontend to the final response.
Fix bugs and perform performance optimizations.
Write deployment scripts and deploy the full stack using Docker Compose to a cloud provider (e.g., Hugging Face Spaces, AWS, GCP).
Tech Focus: Docker, Nginx, Cloud Services.
Milestone: Project "Aura" is live at a public URL and stable for demonstration.
Week 16: Documentation & Presentation
Goal: Complete all project deliverables for submission.
Key Tasks:
Write the final project report in LaTeX, detailing your architecture, methodology, and results.
Record a comprehensive video demo of the live application.
Prepare and rehearse your final presentation.
Tech Focus: LaTeX, Presentation Software.
Milestone: The project is fully documented and submitted.

