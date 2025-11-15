# v3.1 API Server Dockerfile
FROM continuumio/miniconda3:latest
WORKDIR /app

# Install dependencies
COPY environment.yml environment.yml
RUN conda env update -n base -f environment.yml

# Install the project package
COPY setup.py setup.py
RUN pip install .

# Copy all code (src/ and app/)
COPY . .

# API Ports
EXPOSE 80

# Start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]