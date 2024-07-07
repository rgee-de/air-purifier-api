# README for Philips AC2889/10 Air Purifier Backend

This project provides a backend API to interact with a Philips AC2889/10 air purifier. The API allows you to control the
air purifier and observe its status using various endpoints. The backend is designed to run in a Docker container for
easy deployment.

## Table of Contents

- [Requirements](#requirements)
- [Setup and Configuration](#setup-and-configuration)
    - [Environment Variables](#environment-variables)
    - [Running the Docker Container](#running-the-docker-container)
        - [PowerShell Script](#powershell-script)
        - [Bash Script](#bash-script)
    - [Running the Application](#running-the-application)
- [Status Observer](#status-observer)
- [API Endpoints](#api-endpoints)
    - [Control Endpoints](#control-endpoints)
    - [Status Endpoints](#status-endpoints)
    - [WebSocket Endpoint](#websocket-endpoint)
- [Running the Observer Process](#running-the-observer-process)
- [Project Structure](#project-structure)
- [Additional Information](#additional-information)

## Requirements

- Python 3.8 or higher
- Docker
- aioairctrl utility for interacting with the air purifier
- FastAPI framework
- Uvicorn ASGI server

## Setup and Configuration

### Environment Variables

Change the .env file in the root directory

- HOST_IP: The IP address of your air purifier on the network.
- LOG_LEVEL: The logging level (ERROR or INFO).
- ORIGINS: CORS Origins.
- WEBSOCKET_URL: URL where the server runs.

### Running the Docker Container

To deploy the backend in a Docker container, use the provided scripts.

#### PowerShell Script

Run the following command in PowerShell to deploy the container:

```powershell
cd scripts
.\deploy-container.ps1
```

#### Bash Script

Run the following command in a Unix-like terminal to deploy the container:

```shell
cd scripts
.\deploy-container.sh
```

### Running the Application

To run the application locally without Docker, follow these steps:

1. Install the required Python packages:
    ```shell
    pip install -r requirements.txt
    ```

2. Start the FastAPI application:
    ```shell
    uvicorn app.main:app --host 0.0.0.0 --port 8000
    ```

### Status Observer

The status observer process is responsible for periodically fetching the status of the air purifier. This process
restarts every 5 minutes to ensure stability.

To run the status observer manually, execute the following command:

 ```shell
 python app/services/status_observe.py
 ```

## API Endpoints

### Control Endpoints

- POST /mode_p: Set the air purifier to 'P' mode.
- POST /mode_a: Set the air purifier to 'A' mode.
- POST /turbo: Set the air purifier to turbo mode.
- POST /sleep: Set the air purifier to sleep mode.
- POST /stop: Stop the air purifier.
- POST /start: Start the air purifier.

### Status Endpoints

- GET /status: Retrieve the latest status of the air purifier.

### WebSocket Endpoint

- GET /ws: WebSocket endpoint for real-time status updates.

## Running the Observer Process

The observer process continuously monitors the status of the air purifier and restarts every 5 minutes. It can be
started manually or is automatically started when running the main application.

## Project Structure

 ```text
.
├── app
│   ├── config.py                  # Configuration settings
│   ├── main.py                    # Main FastAPI application
│   ├── routes
│   │   ├── control.py             # Control endpoints
│   │   └── status.py              # Status endpoint
│   ├── services
│   │   ├── status_observe.py      # Status observer service
│   │   └── websocket_manager.py   # WebSocket manager service
│   ├── templates
│   │   └── websocket_example.html # WebSocket example HTML
│   └── utils
│       └── globals.py             # Global variables and instances
├── models
│   └── status.py                  # Status model
├── scripts
│   ├── deploy-container.ps1       # PowerShell deployment script
│   ├── deploy-container.sh        # Bash deployment script
│   └── remove-container.ps1       # PowerShell remove script (not shown)
├── .env                           # Environment variables file
├── Dockerfile                     # Docker configuration file
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
 ```

## Additional Information

This backend is designed specifically for the Philips AC2889/10 air purifier. Due to the instability of the purifier's
interface, commands may not always be executed, and status observation may fail. The observer process is restarted every
5 minutes to maintain stability.
