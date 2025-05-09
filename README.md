# Smart Route Planner

A Streamlit application for optimized route planning with LLM-powered extraction capabilities.

## Features

- Intelligent route optimization
- LLM-based data extraction with rule-based fallback
- Interactive map visualization
- Custom route optimization algorithms
- Travel time and distance calculations

## Prerequisites

- Python 3.8+
- PIP package manager
- Hugging Face API key (for LLM extraction features)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smart-route-planner.git
   cd smart-route-planner
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables

Create a `.env` file in the root directory and add the following:

```
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here

```

## Obtaining a Google Maps API Key

1. Go to the Google Cloud Console
2. Create a new project (or select an existing one)
3. Navigate to "APIs & Services" > "Dashboard"
4. Click "+ ENABLE APIS AND SERVICES" at the top
5. Search for and enable these APIs:

```
Directions API
Maps API
```

6. Go to "APIs & Services" > "Credentials"
7. Click "Create credentials" > "API key"
8. Copy the generated API key
9. (Optional but recommended) Restrict the API key usage to your specific APIs and domains
10. Add the key to your .env file


## Obtaining an OpenRouter API Key

1. Go to OpenRouter.ai
2. Create an account or log in
3. Navigate to the API Keys section
4. Click "Create API Key"
5. Name your key and set appropriate rate limits
6. Copy the generated API key
7. Add the key to your .env file

## Usage

1. **Start the Streamlit application**
   ```bash
   python -m streamlit run app.py
   ```

2. **Access the application**
   
   Open your web browser and navigate to:
   ```
   http://localhost:8501
   ```


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

