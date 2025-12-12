# Test script to verify authentication approach on Linux
$body = @{
    grant_type = 'client_credentials'
    client_id = ''
    client_secret = ''
    scope = 'https://graph.microsoft.com/.default'
}

Write-Host "Testing token request format..."
Write-Host "Tenant ID: e8b875bc-6cf4-4c2e-9ded-1371aaf26563"
Write-Host "Client ID: 06f0fb4c-e259-4fbf-bccd-bd672efb344a"
Write-Host "Body parameters: $($body.Keys -join ', ')"
