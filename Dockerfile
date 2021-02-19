FROM python:3

WORKDIR /app
COPY server.py /app/server.py

ENTRYPOINT [ "python", "/app/server.py", "8000" ]
