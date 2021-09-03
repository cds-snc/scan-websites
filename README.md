# Scan Websites

On-demand scanning of websites for accessibility and security vulnerabilities/compliance / Analyse à la demande des sites Web pour les vulnérabilités/conformité en matière d'accessibilité et de sécurité

## Run Locally

Run this in a dev container. 

To interact with aws localstack `use` laws

### Example - List buckets

```bash
laws s3api list-buckets
``` 

### Example - View SNS messages as they get posted
```bash
docker ps
docker logs --follow [localstack CONTAINER_ID]
```