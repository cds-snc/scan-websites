# Scan Websites

On-demand scanning of websites for accessibility and security vulnerabilities/compliance / Analyse à la demande des sites Web pour les vulnérabilités/conformité en matière d'accessibilité et de sécurité

## Run Locally

Run this in a dev container. 

To interact with aws localstack `use` laws

### Seed local database

`cd api && make seed`

### Example - List buckets

```bash
laws s3api list-buckets
laws s3api list-objects --bucket oswasp-zap-report-data --prefix Reports
``` 

### Example - Create folder, copy file, and delete file

```bash
laws s3api put-object --bucket owasp-zap-report-data --key Reports/
laws s3 cp zap_report.json s3://owasp-zap-report-data/Reports/
laws s3 rm s3://owasp-zap-report-data/Reports/zap_report.json
```

### Example - View SNS messages as they get posted
```bash
docker ps
docker logs --follow [localstack CONTAINER_ID]
```