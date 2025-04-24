# A3 Application Instructions

## Initial Setup

1. **Prerequisites**
   - Python 3.x installed
   - Git (for cloning the repository)
   - OpenAI API key

2. **Environment Setup**
   From the root directory (A3):
   ```bash
   # Activate the virtual environment
   source a3-ingestion/.venv/bin/activate
   
   # Your terminal should now show (.venv) at the beginning of the prompt
   # Example: (.venv) username@computer A3 %
   ```

3. **Install Dependencies**
   ```bash
   # Make sure you're in the virtual environment first
   cd a3-ingestion
   pip install -r requirements.txt
   pip install streamlit  # Required but not in requirements.txt
   ```

4. **Configuration**
   - Create or edit `config.env` in the a3-ingestion directory
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

## Running the Application

1. **Start the Streamlit Interface**
   ```bash
   # Exact sequence from root directory:
   cd a3-ingestion
   source .venv/bin/activate
   streamlit run streamlit_app.py
   
   # You should see: "You can now view your Streamlit app in your browser."
   ```
   - The application will automatically open in your default web browser
   - If it doesn't, you can manually visit: http://localhost:8501

2. **Using the Application**
   - Upload size guide images (JPG, JPEG, or PNG)
   - Fill in the metadata:
     - Brand name
     - Gender
     - Size guide header
     - Source URL
     - Unit of measurement
     - Size guide scope
   - Click "Submit for Analysis" to process the image

## Shutting Down

1. **Stop the Streamlit Server**
   - Press `Ctrl+C` in the terminal where Streamlit is running

2. **Deactivate the Virtual Environment**
   ```bash
   deactivate
   ```

## Troubleshooting

1. **Virtual Environment Issues**
   If the virtual environment doesn't exist:
   ```bash
   cd a3-ingestion
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install streamlit
   ```

3. **OpenAI API Issues**
   - Verify your API key is correctly set in config.env
   - Ensure you have sufficient API credits