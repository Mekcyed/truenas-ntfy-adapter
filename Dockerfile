ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim

USER root

RUN apt-get update && \
    apt-get upgrade -y 

WORKDIR /app

COPY ntfy-adapter.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

# start the adapter
CMD ["python", "ntfy-adapter.py"]

