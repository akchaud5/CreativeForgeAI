# 🚀 Creative AI Pipeline

A powerful end-to-end application that transforms text prompts into images and 3D models using Openfabric's AI apps and a local LLM.

## 🌟 Overview

This application creates a complete pipeline that:

1. Takes a text prompt from the user (e.g., "Make me a glowing dragon standing on a cliff at sunset")
2. Uses a local LLM to enhance and expand the prompt with creative details
3. Sends the enhanced prompt to Openfabric's Text-to-Image app
4. Takes the resulting image and transforms it into a 3D model using Openfabric's Image-to-3D app
5. Stores all creations in memory for later retrieval and remixing

## 🛠️ Architecture

The application consists of the following components:

- **Main Application (`main.py`)**: Orchestrates the entire process and handles user inputs/outputs
- **LLM Enhancer**: Local language model integration for prompt enhancement
- **Openfabric Integration**: Connects to Openfabric apps for image and 3D model generation
- **Memory System**: Stores and retrieves creations with both short-term and long-term memory
- **File Manager**: Handles storage and retrieval of binary data (images and 3D models)

## 📋 Requirements

- Python 3.8+
- Openfabric SDK
- Access to Openfabric apps:
  - Text-to-Image (App ID: `f0997a01-d6d3-a5fe-53d8-561300318557`)
  - Image-to-3D (App ID: `69543f29-4d41-4afc-7f29-3d51591f11eb`)

## 🚀 Getting Started

### Running Locally

1. Clone the repository
2. Navigate to the `app` directory
3. Run `./start.sh`
4. Access the API at `http://localhost:8888/swagger-ui/#/App/post_execution`

### Running with Docker

1. Build the Docker image:
   ```
   docker build -f app/Dockerfile -t creative-ai-pipeline .
   ```

2. Run the container:
   ```
   docker run -p 8888:8888 creative-ai-pipeline
   ```

3. Access the API at `http://localhost:8888/swagger-ui/#/App/post_execution`

## 🧪 Usage

### Creating an Image and 3D Model

Send a POST request to the `/execution` endpoint with a prompt:

```json
{
  "prompt": "Make me a glowing dragon standing on a cliff at sunset"
}
```

The response will contain paths to the generated image and 3D model:

```json
{
  "type": "creation",
  "memory_id": "550e8400-e29b-41d4-a716-446655440000",
  "original_prompt": "Make me a glowing dragon standing on a cliff at sunset",
  "enhanced_prompt": "Make me a glowing dragon standing on a cliff at sunset, with intricate skin texture, with otherworldly lighting effects, photorealistic, hyperdetailed, dramatic lighting",
  "image_path": "datastore/images/img_550e8400-e29b-41d4-a716-446655440000_20240518123456.png",
  "model_path": "datastore/models/model_550e8400-e29b-41d4-a716-446655440000_20240518123456.glb",
  "message": "Successfully created image and 3D model from your prompt."
}
```

### Retrieving Past Creations

Send queries like:

```json
{
  "prompt": "Show me my recent dragons"
}
```

The system will search memory and return matching creations:

```json
{
  "type": "memory_query",
  "summary": "Found 3 creations matching 'dragons'",
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "timestamp": 1621876543.123,
      "date": "2024-05-18 12:34:56",
      "original_prompt": "Make me a glowing dragon standing on a cliff at sunset",
      "enhanced_prompt": "Make me a glowing dragon standing on a cliff at sunset, with intricate skin texture, with otherworldly lighting effects, photorealistic, hyperdetailed, dramatic lighting",
      "image_path": "datastore/images/img_550e8400-e29b-41d4-a716-446655440000_20240518123456.png",
      "model_path": "datastore/models/model_550e8400-e29b-41d4-a716-446655440000_20240518123456.glb",
      "image_exists": true,
      "image_size": 1024567,
      "model_exists": true,
      "model_size": 5678901,
      "metadata": {
        "tags": ["dragon", "glowing", "cliff", "sunset"]
      }
    },
    // More results...
  ]
}
```

## 🧠 Memory System

The application features a sophisticated memory system:

### Short-Term Memory

- Maintained during the application's runtime
- Provides fast access to recently created items
- Automatically caches results from long-term memory when accessed

### Long-Term Memory

- Persists across application restarts
- Stored in JSON format in `datastore/memory.json`
- Binary files (images and 3D models) stored in `datastore/images/` and `datastore/models/`

### Memory Queries

- The system recognizes memory-related queries using keyword detection
- Supports searching by keywords, filtering by recency, and limiting result count
- Example queries:
  - "Show me my recent creations"
  - "Find dragons with sunset"
  - "Get my last 3 models"

## 🔍 LLM Integration

The application includes a simulated local LLM for prompt enhancement. In a production environment, this would be replaced with a real local LLM like DeepSeek or LLaMA.

The LLM enhancer:
- Analyzes the input prompt
- Determines the appropriate category (landscape, person, object, etc.)
- Adds relevant descriptive details and style enhancements
- Improves the quality of generated images

## 📂 Project Structure

```
app/
├── config/
│   ├── execution.json      # Execution configuration
│   ├── manifest.json       # App manifest
│   ├── properties.json     # Properties configuration
│   └── state.json          # State configuration
├── core/
│   ├── __init__.py
│   ├── file_manager.py     # Manages image and model files
│   ├── llm_enhancer.py     # Local LLM integration
│   ├── memory_manager.py   # Memory system implementation
│   ├── memory_query.py     # Handles memory queries
│   ├── remote.py           # Openfabric remote communication
│   └── stub.py             # Openfabric app integration
├── datastore/
│   ├── images/             # Stored images
│   ├── memory.json         # Persistent memory
│   ├── models/             # Stored 3D models
│   └── tokens.json         # Authentication tokens
├── ignite.py               # Application ignition
├── main.py                 # Main application logic
├── ontology_*/             # Auto-generated schemas
└── start.sh                # Startup script
```

## 🔮 Future Enhancements

- GUI interface with Streamlit or Gradio
- FAISS/ChromaDB for semantic similarity search
- Local 3D model viewer
- Voice-to-text interaction
- Fine-tuning options for the image and 3D generation

## 📄 License

This project is provided as-is without any warranties. Use at your own risk.

## 🙏 Acknowledgements

- Openfabric for providing the AI app infrastructure
- The open-source community for inspiration and tools