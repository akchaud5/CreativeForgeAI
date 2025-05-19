# 🚀 Creative AI Pipeline: Text → Image → 3D

A powerful application that takes user prompts, enhances them with a local LLM, generates images, converts them to 3D models, and remembers everything for future reference.

## 🌟 Features

- **Prompt Enhancement**: Uses a local LLM to expand and enrich user prompts for better image generation
- **Text-to-Image**: Sends enhanced prompts to Openfabric's Text-to-Image service
- **Image-to-3D**: Converts generated images to 3D models through Openfabric's Image-to-3D service
- **Memory System**: Maintains both session memory and persistent storage of all creations
- **Memory Commands**: Interact with past creations through simple commands

## 🏗️ Architecture

```
User Prompt
↓
Local LLM (Prompt Enhancement)
↓
Text-to-Image App (Openfabric)
↓
Image Output
↓
Image-to-3D App (Openfabric)
↓
3D Model Output + Memory Storage
```

## 📦 Components

- **main.py**: Main execution entry point
- **memory/**: Memory-related modules
  - **memory_manager.py**: Core memory functionality (short-term and persistent)
  - **llm_enhancer.py**: LLM integration for prompt enhancement
  - **file_manager.py**: Handles image and 3D model storage
  - **memory_query.py**: Interface for querying stored memories

## 🚀 Usage

### Starting the Application

```bash
# Run locally
./start.sh

# Or with Docker
docker build -t creative-ai-app .
docker run -p 8888:8888 creative-ai-app
```

### Using the API

Access the Swagger UI at: http://localhost:8888/swagger-ui/#/App/post_execution

#### Basic Prompt

```json
{
  "prompt": "A majestic dragon flying over a medieval castle"
}
```

#### Memory Commands

```json
{
  "prompt": "memory"
}
```

Lists your recent memory entries.

```json
{
  "prompt": "memory id [memory-id]"
}
```

Retrieves a specific memory by ID.

```json
{
  "prompt": "memory search dragon"
}
```

Searches memories containing "dragon" in the prompts.

## 💾 Memory System

The application features a dual-layer memory system:

1. **Short-term Memory (SessionMemory)**:
   - In-memory storage during runtime
   - Fast access to recent creations
   - Resets when the application restarts

2. **Long-term Memory (PersistentMemory)**:
   - File-based storage in JSON format
   - Persists across application restarts
   - Indexed for efficient retrieval

For each creation, the system stores:
- Original user prompt
- Enhanced prompt
- Path to the generated image
- Path to the generated 3D model
- Timestamp
- User ID

## 🛠️ Configuration

The application uses two Openfabric services:
- Text-to-Image App ID: `f0997a01-d6d3-a5fe-53d8-561300318557`
- Image-to-3D App ID: `69543f29-4d41-4afc-7f29-3d51591f11eb`

These IDs are configured in `main.py`.

## 🧪 Example Workflow

1. User submits prompt: "A cyberpunk city at night"
2. LLM enhances it to include details about neon lights, skyscrapers, etc.
3. Text-to-Image service creates a detailed image
4. Image-to-3D service converts it to a 3D model
5. All data is stored in both session and persistent memory
6. User can retrieve or search for the creation later

## 🔮 Future Enhancements

- Advanced LLM integration with fine-tuned models
- Similarity search for memories using embeddings
- Web interface with 3D viewer
- Voice-to-text input capabilities