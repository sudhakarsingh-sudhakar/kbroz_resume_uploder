# Use the official Python base image
FROM python:3.9-slim
 
# Set the working directory inside the container
WORKDIR /kbroz_resume_uploder
 
# Copy the requirements.txt file into the container
COPY requirements.txt .
 
# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy the rest of your application code into the container
COPY . .
EXPOSE 8000
# Set the default command to run your script
CMD ["python", "run.py", "0.0.0.0:8000"]