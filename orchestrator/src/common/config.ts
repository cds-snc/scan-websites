export const scanTaskArns = {
  "owasp-zap": process.env.OWASP_ZAP_TASK_DEF_ARN,
  nuclei: process.env.NUCLEI_TASK_DEF_ARN,
} as const;

export const scanReportBuckets = {
  "owasp-zap": process.env.OWASP_ZAP_REPORT_DATA_BUCKET,
  nuclei: process.env.NUCLEI_REPORT_DATA_BUCKET, // Placeholder; Will get its own after this refactor
} as const;
