# Azure Services Cost Calculator for M365 Security Toolkit
# Based on East US 2 pricing (October 2025)

## Recommended Production Configuration (~$100/month)

### Core Services
- **Resource Group**: FREE
- **Storage Account (Standard_LRS)**: $25/month
  - 100GB blob storage
  - 10,000 transactions/month
  - Stores audit reports, CSV files, dashboards

- **Key Vault (Standard)**: $5/month
  - 10,000 operations/month
  - Stores M365 credentials, API keys securely

- **Container Registry (Basic)**: $5/month
  - 10GB storage
  - Unlimited pulls for private images

- **Log Analytics Workspace**: $20/month
  - 10GB data ingestion/month
  - 31-day retention

- **Application Insights**: $10/month
  - Application performance monitoring
  - Custom telemetry

- **Container Apps (Consumption)**: $35/month
  - Serverless container execution
  - Automatic scaling
  - Pay-per-execution for scheduled audits

### Additional Considerations

#### Data Transfer Costs
- **Outbound Data Transfer**: $0.09/GB after 5GB free
- **Estimate**: $5-10/month for report downloads

#### Backup & Disaster Recovery
- **Geo-Redundant Storage**: +$15/month
- **Key Vault Backup**: $1/month

#### Development Environment
- **Separate resource group**: +$30/month
- **Total with dev environment**: ~$130/month

### Cost Optimization Tips

1. **Use Consumption Plans**: Pay only when running audits
2. **Set up Budgets**: Alert at $80 to prevent overruns  
3. **Use Reserved Instances**: 30% savings for steady workloads
4. **Clean up old data**: Implement lifecycle policies
5. **Monitor usage**: Use Azure Cost Management

### Scaling Factors
- **Per 1000 users audited**: +$5-10/month
- **Daily vs Weekly audits**: 4x cost difference
- **Multiple tenants**: +$20-30/month per tenant
- **Advanced analytics**: +$50-100/month

## Quick Deployment Commands

# Deploy minimal infrastructure ($58/month)
.\Deploy-Infrastructure.ps1 -SubscriptionId "your-sub-id" -ResourceGroupName "rg-m365-security-dev" -AdminUserPrincipalName "admin@contoso.com" -Environment "dev"

# Deploy production infrastructure ($100/month)  
.\Deploy-Infrastructure.ps1 -SubscriptionId "your-sub-id" -ResourceGroupName "rg-m365-security-prod" -AdminUserPrincipalName "admin@contoso.com" -Environment "prod"