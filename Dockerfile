# Step 1: Start with a modern Python 3.12 operating system (lightweight 'slim' version)
FROM python:3.12-slim

# Step 2: Set the folder inside the container where our app will live
WORKDIR /app

# Step 3: Copy the requirements file from your machine INTO the container
COPY requirements.txt .

# Step 4: Install all the Python libraries listed in requirements.txt
# This ensures AutoGen, Streamlit, and dotenv are inside the image.
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy all your other project files (app.py, agents_config.py, etc.)
# into the container's /app folder. (Remember: .gitignore stops secrets from being copied!)
COPY . .

# Step 6: Streamlit needs Port 8501 exposed to allow users to access the UI
EXPOSE 8501

# Step 7: The default command to run when the container starts.
# This launches the Streamlit server automatically.
CMD ["streamlit", "run", "app.py"]