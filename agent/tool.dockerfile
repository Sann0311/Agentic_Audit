# 1. Base image
FROM python:3.10-slim

# 2. Set working directory
WORKDIR /app

# 3. Install only the packages your tools & LLM client need
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    pandas \
    openpyxl \
    pydantic \
    google-adk \
    litellm \
    grpcio-status==1.48.2

# 4. Copy your agent code into the image
COPY . .

# 5. (Optional) Expose the port your agent listens on
EXPOSE 8000

# 6. Default command to launch your multi‑tool agent
CMD ["python", "-m", "multi_tool_agent"]
