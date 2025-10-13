# RainSafe Backend Development Container

This directory contains the development container configuration for the RainSafe backend.

## Features

- **Python 3.11** with FastAPI and all required dependencies
- **MongoDB 6** database with health checks
- **VS Code extensions** for Python development
- **Auto-reload** for development
- **Health checks** for both backend and database
- **Volume mounting** for live code editing

## Usage

### Using VS Code Dev Containers

1. Open the project in VS Code
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Select "Dev Containers: Reopen in Container"
4. Wait for the container to build and start
5. The backend will be available at `http://localhost:8000`

### Using Docker Compose

```bash
# Start the development environment
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the environment
docker-compose down
```

## Services

- **Backend**: FastAPI application on port 8000
- **MongoDB**: Database on port 27017

## Environment Variables

The container uses the `.env` file in the backend directory. Make sure to set:

- `MONGO_URI`: MongoDB connection string
- `OPENWEATHER_API_KEY`: OpenWeather API key (optional for development)

## Development

The container automatically reloads when you make changes to the code. The MongoDB data is persisted in a Docker volume.

## Troubleshooting

1. **Container won't start**: Check the logs with `docker-compose logs`
2. **Database connection issues**: Ensure MongoDB is healthy before the backend starts
3. **Port conflicts**: Make sure ports 8000 and 27017 are available

