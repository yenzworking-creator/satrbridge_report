
# Use the official Python 3.9 image
FROM python:3.9-slim

# Set the working directory to /code
WORKDIR /code

# Copy the current directory contents into the container at /code
COPY . /code

# Install requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Create a non-root user and switch to it (Security Best Practice for HF Spaces)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# Prepare working directory permissions (if needed for temporary files)
# But since we are user 1000 and WORKDIR is /code, we might need write access to some folders if app writes files.
# The app writes to 'static/reports' and 'data/'. Let's unsure they are writable.
USER root
RUN chown -R user:user /code
USER user

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port 7860 (Hugging Face Spaces default)
EXPOSE 7860

# Run the application with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]
