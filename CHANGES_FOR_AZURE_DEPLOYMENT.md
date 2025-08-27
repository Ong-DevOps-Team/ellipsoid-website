# Changes for Azure Deployment - Ellipsoid Labs Website

This document captures all the changes, configurations, and learnings required to successfully deploy the Ellipsoid Labs website to Azure with proper frontend-backend communication.

## Table of Contents

1. [GitHub Actions Workflow Changes](#github-actions-workflow-changes)
2. [Frontend Environment Variable Configuration](#frontend-environment-variable-configuration)
3. [Backend CORS Configuration](#backend-cors-configuration)
4. [Azure Service Configuration](#azure-service-configuration)
5. [Key Learnings and Troubleshooting](#key-learnings-and-troubleshooting)
6. [Deployment Checklist](#deployment-checklist)

## 1. GitHub Actions Workflow Changes

### Modified Files:
- `.github/workflows/azure-static-web-apps-orange-ground-0080e851e.yml`

### Changes Made:

#### Environment Variables in Build Process
Added a step to set `REACT_APP_API_URL` during the GitHub Actions build:

```yaml
- name: Set Environment Variables
  run: |
    echo "REACT_APP_API_URL=https://ellipsoid-backend-dzasfua8c7gjeshd.westus-01.azurewebsites.net" >> $GITHUB_ENV
    echo "REACT_APP_ENVIRONMENT=production" >> $GITHUB_ENV
    echo "REACT_APP_DEBUG=false" >> $GITHUB_ENV
```

**Why this was necessary:**
- Azure Static Web Apps doesn't automatically load `.env.production` files
- The GitHub Actions runner needs explicit environment variable setting
- This bypasses Create React App's environment file loading mechanism

I also needed to modify main_ellispoid-backend.yml to add requirements.txt explictly and remove the "!*.txt.  I commented out the running of pip earlier in the process as it was failing, and added this 
to the App Service Config Startup Command:
python -m pip install -r requirements.txt && cd backend && uvicorn main:app --host 0.0.0.0 --port 8000


## 2. Frontend Environment Variable Configuration

### Key Issue:
**React's default `env.production` file was not being loaded in Azure Static Web Apps builds.**

### Root Cause:
- Azure Static Web Apps uses Oryx build system, not standard Create React App
- `NODE_ENV=production` was not being set in the build environment
- Environment files were being ignored by the Azure build process

### Solution:
- Set `REACT_APP_API_URL` directly in GitHub Actions workflow (see above)
- This ensures the frontend knows the correct backend URL in production

### Files Involved:
- `.github/workflows/azure-static-web-apps-orange-ground-0080e851e.yml` (environment variables)
- `frontend/env.production` (exists but not used by Azure)
- `frontend/src/config.js` (reads `process.env.REACT_APP_API_URL`)

## 3. Backend CORS Configuration

### Modified Files:
- `backend/main.py`

### Key Changes:

#### CORS Allow Origins Configuration
Updated from overly permissive to secure minimal allowlist:

```python
# BEFORE (overly permissive)
allow_origins=[
    "http://localhost:3000",
    "https://*.azurestaticapps.net",        # ❌ RISKY - allows any Azure Static Web App
    "https://*.azurewebsites.net",          # ❌ RISKY - allows any Azure Web App
    "https://ellipsoid-labs.azurestaticapps.net",
    "https://www.ellipsoid-labs.com",
    "https://ellipsoid-labs.com"
]

# AFTER (secure minimal)
allow_origins=[
    "http://localhost:3000",                                    # ✅ Development only
    "https://orange-ground-0080e851e.2.azurestaticapps.net",   # ✅ Actual frontend domain
    "https://www.ellipsoid-labs.com",                          # ✅ Planned custom domain
    "https://ellipsoid-labs.com"                               # ✅ Planned custom domain
]
```

#### CORS Security Improvements:
- Removed wildcard domains (`*.azurestaticapps.net`, `*.azurewebsites.net`)
- Added specific frontend domain discovered through debugging
- Added planned custom domains proactively
- Followed principle of least privilege

### Debugging CORS Issues:
Added temporary debug middleware to log request origins:

```python
class DebugCORSMiddleware(CORSMiddleware):
    async def dispatch(self, request, call_next):
        origin = request.headers.get("origin", "No Origin")
        info(f"CORS DEBUG: Request from origin: {origin}, path: {request.url.path}, method: {request.method}")
        return await super().dispatch(request, call_next)
```

## 4. Azure Service Configuration

### Backend URL:
`https://ellipsoid-backend-dzasfua8c7gjeshd.westus-01.azurewebsites.net`

### Frontend URL (Current):
`https://orange-ground-0080e851e.2.azurestaticapps.net`

### Planned Custom Domain:
- `www.ellipsoidlabs.com`
- `ellipsoidlabs.com`

### Azure Services Used:
- **Azure Static Web Apps**: Frontend hosting and CI/CD
- **Azure Web Apps**: Backend API hosting
- **Azure Container Registry**: (if using custom containers)

## 5. Key Learnings and Troubleshooting

### Critical Discoveries:

1. **Environment Variable Loading**:
   - Azure Static Web Apps ignores `.env` files
   - Must set environment variables in GitHub Actions workflow
   - Create React App's environment file loading doesn't work in Azure

2. **CORS Domain Matching**:
   - Wildcard patterns like `*.azurestaticapps.net` don't always match specific subdomains
   - Must use exact domain names discovered through debugging
   - Custom domains require explicit CORS configuration

3. **Build Process Differences**:
   - Local `npm run build` ≠ Azure Oryx build process
   - GitHub Actions environment ≠ local development environment
   - Must test with actual deployed URLs

4. **Debugging Strategy**:
   - Add console.log statements to frontend for debugging
   - Add debug logging to backend CORS middleware
   - Use browser network tab to inspect CORS headers
   - Test backend health endpoint independently

### Common Issues and Solutions:

#### Issue: "No 'Access-Control-Allow-Origin' header"
**Solution**: Add specific domain to CORS allow_origins list

#### Issue: REACT_APP_API_URL is undefined in production
**Solution**: Set environment variables in GitHub Actions workflow

#### Issue: Backend responding 200 OK but frontend gets CORS error
**Solution**: Check that exact domain is in CORS allow_origins

#### Issue: Login fails with "Authentication failed"
**Solution**: Verify CORS allows credentials and specific domain

### Testing Checklist:
1. Backend health check: `curl https://backend-url/health`
2. Frontend environment variables in browser console
3. CORS headers in browser network tab
4. Login functionality end-to-end
5. About page loading (non-authenticated endpoint)

## 6. Deployment Checklist

NOTE: Powershell health check call to backend API:
Invoke-WebRequest -Uri "https://ellipsoid-backend-dzasfua8c7gjeshd.westus-01.azurewebsites.net/health" -Method GET

Response:
StatusCode        : 200
StatusDescription : OK
Content           : {"status":"healthy"}
RawContent        : HTTP/1.1 200 OK
                    Content-Length: 20
                    Content-Type: application/json
                    Date: Sat, 23 Aug 2025 05:51:51 GMT
                    Server: uvicorn

                    {"status":"healthy"}
Forms             : {}
Headers           : {[Content-Length, 20], [Content-Type, application/json], [Date, Sat, 23 Aug 2025 05:51:51 GMT],     
                    [Server, uvicorn]}
Images            : {}
InputFields       : {}
Links             : {}
ParsedHtml        : mshtml.HTMLDocumentClass
RawContentLength  : 20

### Pre-Deployment:
- [ ] Verify backend is deployed and healthy
- [ ] Update REACT_APP_API_URL in GitHub Actions workflow
- [ ] Configure CORS with correct frontend domains
- [ ] Test backend endpoints independently

### Deployment:
- [ ] Commit changes to git
- [ ] Push to GitHub (triggers Azure deployment)
- [ ] Monitor GitHub Actions workflow
- [ ] Verify both frontend and backend deployments complete

### Post-Deployment Testing:
- [ ] Test About page (non-authenticated)
- [ ] Test login functionality
- [ ] Verify console shows correct API URL
- [ ] Check browser network tab for successful requests
- [ ] Test custom domain when configured

### Security Verification:
- [ ] Confirm CORS allows only intended domains
- [ ] Verify no sensitive data in environment variables
- [ ] Check that debug logging is removed in production

## Summary

The key changes required for Azure deployment were:

1. **Set environment variables in GitHub Actions** (not .env files)
2. **Use specific domain names in CORS** (not wildcards)
3. **Add debugging capabilities** for troubleshooting
4. **Follow principle of least privilege** for security

These changes ensure the frontend can properly communicate with the backend in the Azure environment, with proper security and debugging capabilities.

**Remember**: Always test with the actual deployed URLs, as local development and Azure environments behave differently.
