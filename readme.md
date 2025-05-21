# 🚀 CreativeForge AI: Text to 3D Pipeline

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
- **LLM Enhancer**: Multiple options for prompt enhancement:
  - Simulated LLM (rule-based enhancer)
  - Real DeepSeek 6.7B LLM integration
  - Lightweight rule-based alternative (low memory usage)
- **Openfabric Integration**: Connects to Openfabric apps for image and 3D model generation
- **Memory System**: Stores and retrieves creations with both short-term and long-term memory
- **File Manager**: Handles storage and retrieval of binary data (images and 3D models)
- **Web Interface**: User-friendly Streamlit interface for interacting with the pipeline, including voice input capability

## 📋 Requirements

- Python 3.8+
- Openfabric SDK
- Streamlit (for web interface)
- PyTorch and Transformers (for DeepSeek LLM option)
- Access to Openfabric apps:
  - Text-to-Image (App ID: `f0997a01-d6d3-a5fe-53d8-561300318557`)
  - Image-to-3D (App ID: `69543f29-4d41-4afc-7f29-3d51591f11eb`)

## 🚀 Getting Started

### Running the Web Interface

You have three options for running the web interface:

#### 1. Simulated LLM (Default)
```
./run_web_app.sh
```

#### 2. Real DeepSeek LLM (Requires 16GB+ RAM or GPU)
```
./run_web_app_real_llm.sh
```

#### 3. Lightweight Rule-Based (For Low-Memory Environments)
```
./run_web_app_lite.sh
```

### Running with Google Colab

For powerful GPU acceleration without local hardware requirements:

1. Create a new Colab notebook and clone the repository
2. Install dependencies:
   ```python
   !pip install transformers accelerate bitsandbytes torch streamlit
   ```
3. Run the app with ngrok or Colab's built-in port forwarding

### Running the API Locally

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

### Web Interface

The web interface provides a user-friendly way to interact with the pipeline:

1. **Creation Tab**:
   - Enter your prompt in the text area or use voice input
   - Choose between text or voice input with the radio buttons
   - Click "Generate" to create an image and 3D model
   - View the results and download the 3D model

2. **Search Tab**:
   - Enter a search query using text or voice input
   - Toggle between input methods with the radio buttons
   - Browse through results with details and media

### API Usage

#### Creating an Image and 3D Model

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

#### Retrieving Past Creations

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

## 🔍 LLM Integration Options

### 1. Simulated LLM (Default)

- Lightweight rule-based system that simulates an LLM
- Suitable for any system with minimal resource requirements
- Categorizes prompts and adds relevant enhancements

### 2. DeepSeek LLM (Advanced)

- Integrates DeepSeek 6.7B instruct model for high-quality prompt enhancement
- Provides more creative and contextual prompt expansions
- Requires significant RAM (16GB+) or a GPU
- Uses 4-bit quantization to reduce memory requirements

### 3. Lightweight Rule-Based (Low-Memory)

- Optimized version for systems with limited memory
- Uses templates and randomized enhancements
- Provides good results without large model overhead
- Perfect for deployment on resource-constrained environments

## 📂 Project Structure

```
app/
├── config/                    # Application configuration
├── core/                      # Core functionality
│   ├── file_manager.py        # Manages image and model files
│   ├── llm_enhancer.py        # Simulated LLM prompt enhancement
│   ├── real_llm_enhancer.py   # DeepSeek LLM integration
│   ├── lite_llm_enhancer.py   # Lightweight rule-based enhancer
│   ├── memory_manager.py      # Memory storage and retrieval
│   ├── memory_query.py        # Memory query processing
│   ├── remote.py              # Remote API communication
│   └── stub.py                # Openfabric SDK integration
├── datastore/                 # Data storage directory
├── ontology_*/                # Auto-generated schemas
├── openfabric_pysdk/          # Mocked Openfabric SDK
├── main.py                    # Main application entry point
├── web_app.py                 # Streamlit web interface (simulated LLM)
├── web_app_real_llm.py        # Streamlit web interface with DeepSeek
├── web_app_lite.py            # Streamlit web interface (low memory)
├── test_memory.py             # Memory system tests
├── test_pipeline.py           # Pipeline tests
└── simple_test.py             # Simple test harness
```

## 🔮 Future Enhancements

- FAISS/ChromaDB for semantic similarity search
- Local 3D model viewer with interactive controls
- ✅ Voice-to-text interaction (implemented)
- Fine-tuning options for the image and 3D generation
- API key configuration management
- Additional LLM options (Llama, Mistral, etc.)

## 📄 License

This project is provided as-is without any warranties. Use at your own risk.

## 🙏 Acknowledgements

- Openfabric for providing the AI app infrastructure
- DeepSeek AI for the open-source LLM model
- The open-source community for inspiration and tools
- Streamlit for the interactive web interface