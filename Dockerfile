FROM python:3.11-slim

WORKDIR /app

ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000
ENV MCP_PATH=/mcp
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY mcp_server ./mcp_server

EXPOSE 8000

CMD ["python", "mcp_server/routes.py"]
