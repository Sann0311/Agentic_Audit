# backend/backend.dockerfile

FROM python:3.10-slim
WORKDIR /app

# Install FastAPI/Uvicorn + ADK client + your agent deps
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    httpx \
    google-adk \
    litellm \
    grpcio-status==1.48.2 \
    pandas \
    openpyxl \
    pydantic

# Copy in your backend code
COPY . .

# Expose FastAPI port
EXPOSE 5000

# Timezone setup (optional)
ENV TZ=America/Toronto
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*

# Start Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]
