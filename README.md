# Scan Websites

On-demand scanning of websites for accessibility and security vulnerabilities/compliance / Analyse à la demande des sites Web pour les vulnérabilités/conformité en matière d'accessibilité et de sécurité

## Adding new scans

- Create new alembic database migration to insert new scan_type
- Add new scan_type to AvailableScans class in `/pub_sub/`
- Associate validator_list to new scan_type in `/pub_sub/`
- Add new SNS topic for the new scan (api terraform)
- Add new S3 report bucket via terraform + IAM permissions to store results for processing by the api (api terraform)
- Add new lambda function via terraform + IAM permissions to be invoked by SNS
- Update api terraform `outputs.tf` to include newly created items
- Create a new lambda nodejs project in `/scanners/`
   - If using ECS
     - Create a runner under `/runners/`. This will be invoked by your nodejs lambda.
     - Create ECS task definition TF and associated container definition `.json`
- Create new entries for your scanner under the various actions in `/.github/`
   - TF plan (CI only)
   - TF apply (Make changes to Production)
   - Build container to test dockerbuild (CI only)
   - Build and push container to ECR (Push to Production)
- Profit :tada:

## Run Locally

Run this in a dev container. 

To interact with aws localstack `use` laws

### Initial Run Reqs
`cd api && make install && make install-dev`

#### VS Code Path Env
`export PATH="$PATH:/home/vscode/.local/bin/"`

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