# Operations Guide

## Deployment

1. Ensure Docker and Docker Compose are installed.
2. Push changes to the `main` branch to trigger the **Deploy** GitHub Actions workflow, which builds and pushes a Docker image to GitHub Container Registry.
3. To run the application locally:
   ```bash
   docker compose up --build
   ```

## Logging Stack

1. Start the ELK stack alongside the application logs:
   ```bash
   docker compose -f docker-compose.logging.yml up
   ```
2. The application writes logs to the `./logs` directory. Filebeat forwards these logs to Logstash, which indexes them in Elasticsearch.
3. Access Kibana at <http://localhost:5601> to explore logs.

## Testing and Linting

- Lint code with `flake8 jarvis/logging` and `black --check jarvis/logging` or rely on the **Lint** workflow.
- Run tests locally with `pytest` or via the **Test** workflow.
