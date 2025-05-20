# Jester Setup and Usage Instructions

## 1. Virtual Environment Setup

### First Time Setup
```bash
# Create a new virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On Mac/Linux
# or
.\venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Subsequent Uses
```bash
# Just activate the virtual environment
source venv/bin/activate  # On Mac/Linux
# or
.\venv\Scripts\activate  # On Windows
```

## 2. Database Access

### Supabase Web Interface
1. Go to [app.supabase.com](https://app.supabase.com)
2. Log in to your account
3. Select the "jester-db" project
4. Use either:
   - **Table Editor**: For visual database management
   - **SQL Editor**: For running SQL queries

### Using Postico (Mac)
1. Open Postico
2. Click "New Favorite" (⌘N)
3. Enter connection details:
   - Host: `db.lntahfecexbduagqdhrr.supabase.co`
   - Port: `5432`
   - Database: `postgres`
   - User: `postgres`
   - Password: `efVtower12`
4. Click "Connect"

## 3. Running the Application

### Start Streamlit
```bash
# Make sure your virtual environment is activated
streamlit run app/ui/streamlit_app.py
```

The application will be available at: http://localhost:8501

### Database Connection Test
To verify database connectivity:
```bash
python scripts/test_db.py
```

## 4. Environment Variables
Make sure your `.env` file contains:
```
DATABASE_URL=postgresql://postgres:efVtower12@db.lntahfecexbduagqdhrr.supabase.co:5432/postgres
OPENAI_API_KEY=your_openai_api_key
ENVIRONMENT=development
```

## 5. Troubleshooting

### Database Connection Issues
- Verify your `.env` file has the correct DATABASE_URL
- Check if you can access the database through Supabase web interface
- Run the database test script: `python scripts/test_db.py`

### Streamlit Issues
- Ensure virtual environment is activated
- Check if all dependencies are installed
- Verify port 8501 is not in use

### Virtual Environment Issues
- If you get "command not found", make sure you're in the correct directory
- If dependencies are missing, run `pip install -r requirements.txt` again 