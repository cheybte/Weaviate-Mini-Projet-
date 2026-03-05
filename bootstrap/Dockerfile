FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir requests
COPY init_weaviate.py /app/init_weaviate.py
CMD ["python", "/app/init_weaviate.py"]
