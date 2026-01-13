# SS_PDP

## Deployment on DigitalOcean Droplet

This project can be deployed on a DigitalOcean Droplet (or any server) using Docker Compose.

### Prerequisites

- Docker and Docker Compose installed on your server
- A Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))
- Google Service Account credentials with access to Google Sheets API

### Deployment Steps

1. **Install Docker and Docker Compose** on your droplet:
   ```bash
   # Update package list
   sudo apt-get update
   
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Install Docker Compose
   sudo apt-get install docker-compose-plugin
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/mukhiddinov/SS_PDP.git
   cd SS_PDP
   ```

3. **Create environment file**:
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit with your actual values
   nano .env
   ```
   
   Update the following values in `.env`:
   - `POSTGRES_PASSWORD`: Set a strong password for PostgreSQL
   - `DATABASE_URL`: Update with the same password you set above
   - `BOT_TOKEN`: Your Telegram bot token from @BotFather
   - `GOOGLE_CREDS_JSON`: Your Google Service Account credentials as a single-line JSON string

4. **Start the application**:
   ```bash
   # Build and start all services in detached mode
   sudo docker compose up -d --build
   ```

5. **Verify deployment**:
   ```bash
   # Check if all services are running
   sudo docker compose ps
   
   # Check API health
   curl http://localhost:8000/healthz
   
   # View logs
   sudo docker compose logs -f
   ```

### Service Architecture

The application consists of three services:

- **db**: PostgreSQL database with persistent volume
- **api**: FastAPI application that fetches schedule data from Google Sheets (port 8000)
- **bot**: Telegram bot that interacts with users and calls the API

### Stopping the Application

```bash
sudo docker compose down
```

To stop and remove all data (including the database):
```bash
sudo docker compose down -v
```

### Updating the Application

```bash
# Pull latest changes
git pull

# Rebuild and restart
sudo docker compose up -d --build
```

### Troubleshooting

- Check logs: `sudo docker compose logs -f [service_name]`
- Restart a specific service: `sudo docker compose restart [service_name]`
- View service status: `sudo docker compose ps`

