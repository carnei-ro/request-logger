FROM python:3-alpine

RUN pip install requests

WORKDIR /app
COPY server.py /app/server.py

EXPOSE 8000

ENTRYPOINT [ "python", "/app/server.py", "8000" ]
