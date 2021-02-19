FROM python:3-alpine

WORKDIR /app
COPY server.py /app/server.py

ENTRYPOINT [ "python", "/app/server.py", "8000" ]
