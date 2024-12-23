Inspired by: https://github.com/ZTube/truenas-gotify-adapter

# truenas-ntfy-adapter

Send notifications from TrueNas to ntfy.sh server using a Slack dummy webhook.

## Description

This project provides an adapter to send notifications from TrueNas to an ntfy.sh server. It listens for incoming messages and forwards them to the specified ntfy.sh topic.

## Setup

### Prerequisites

- Docker
- Docker Compose

### Environment Variables

Create a `.env` file in the root directory of the project and configure the following environment variables:

```
NTFY_BASE_URL=https://ntfy.sh
NTFY_TOPIC=ntfy_topic
NTFY_TOKEN=ntfy_token
LISTEN_HOST=0.0.0.0
LISTEN_PORT=8008
```

## Usage

### Running the Application

1. Build and start the Docker container:

```sh
docker-compose up --build
```

2. The application will be available at `http://<LISTEN_HOST>:<LISTEN_PORT>`.

### Setting ntf-proxy as Alert Service in TrueNas

Goto 'Alert Settings' -> 'Add' -> Set Name, select Type 'Slack' and enter the URL/IP of your docker host. Try it with 'Send Test Alert'.
