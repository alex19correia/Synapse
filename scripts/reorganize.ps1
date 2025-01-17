# Create new directory structure
Write-Host "Creating new directory structure..."
$dirs = @(
    "apps/web/src/app",
    "apps/web/src/components",
    "apps/web/src/lib",
    "apps/web/src/styles",
    "apps/web/public",
    "apps/api/src/core",
    "apps/api/src/routes",
    "apps/api/src/services",
    "apps/api/tests",
    "packages/core/src/llm",
    "packages/core/src/rag",
    "packages/core/src/memory",
    "packages/utils/src",
    "docs/api",
    "docs/architecture",
    "docs/development",
    "infrastructure/docker/api",
    "infrastructure/docker/web"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir
}

# Move files using git mv to preserve history
Write-Host "Moving files to new structure..."

# Move frontend files
git mv src/app/* apps/web/src/app/
git mv src/components/* apps/web/src/components/
git mv src/styles/* apps/web/src/styles/

# Move backend files
git mv src/services/* apps/api/src/services/
git mv src/api/* apps/api/src/routes/
git mv src/core/* packages/core/src/

# Move documentation
git mv docs/* docs/architecture/

# Move configuration files
git mv docker-compose.yml infrastructure/docker/
git mv .env.example .env.example

# Create new package.json files
Write-Host "Creating package configuration files..."

# Root package.json
@"
{
  "name": "synapse",
  "private": true,
  "workspaces": [
    "apps/*",
    "packages/*"
  ],
  "scripts": {
    "dev": "pnpm --parallel -r run dev",
    "build": "pnpm --parallel -r run build",
    "test": "pnpm --parallel -r run test",
    "lint": "pnpm --parallel -r run lint"
  }
}
"@ | Out-File -FilePath "package.json" -Encoding UTF8

# Web package.json
@"
{
  "name": "@synapse/web",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "@synapse/core": "workspace:*",
    "@synapse/utils": "workspace:*"
  }
}
"@ | Out-File -FilePath "apps/web/package.json" -Encoding UTF8

# Core package.json
@"
{
  "name": "@synapse/core",
  "version": "0.1.0",
  "private": true,
  "main": "src/index.ts",
  "types": "src/index.ts",
  "scripts": {
    "build": "tsc",
    "test": "jest"
  }
}
"@ | Out-File -FilePath "packages/core/package.json" -Encoding UTF8

Write-Host "Project reorganization complete!"
Write-Host "Please review the changes and commit them to git." 