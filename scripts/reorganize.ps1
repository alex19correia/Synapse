# Create new directory structure
Write-Host "Creating new directory structure..."
$dirs = @(
    "apps/web/src/app",
    "apps/web/src/components",
    "apps/web/src/lib/hooks",
    "apps/web/src/lib/types",
    "apps/web/src/lib/contexts",
    "apps/web/src/styles",
    "apps/web/public",
    "apps/api/src/core",
    "apps/api/src/routes",
    "apps/api/src/services",
    "apps/api/src/config",
    "apps/api/src/models",
    "apps/api/tests",
    "packages/core/src/llm",
    "packages/core/src/rag",
    "packages/core/src/memory",
    "packages/utils/src",
    "infrastructure/docker"
)

foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir
}

# Function to safely move files
function Move-GitFiles {
    param (
        [string]$source,
        [string]$destination
    )
    
    if (Test-Path $source) {
        Write-Host "Moving $source to $destination"
        Copy-Item -Path $source -Destination $destination -Recurse -Force
        git add $destination
        if ($LASTEXITCODE -eq 0) {
            Remove-Item -Path $source -Recurse -Force
        }
    } else {
        Write-Host "Source path not found: $source"
    }
}

Write-Host "Moving files to new structure..."

# Move Next.js app files
Write-Host "Moving Next.js files..."
Move-GitFiles "src/app" "apps/web/src/app"
Move-GitFiles "src/components" "apps/web/src/components"
Move-GitFiles "src/hooks" "apps/web/src/lib/hooks"
Move-GitFiles "src/types" "apps/web/src/lib/types"
Move-GitFiles "src/contexts" "apps/web/src/lib/contexts"

# Move API files
Write-Host "Moving API files..."
Move-GitFiles "src/api" "apps/api/src/routes"
Move-GitFiles "src/services" "apps/api/src/services"
Move-GitFiles "src/core" "apps/api/src/core"
Move-GitFiles "src/config" "apps/api/src/config"
Move-GitFiles "src/models" "apps/api/src/models"

# Move shared packages
Write-Host "Moving shared packages..."
Move-GitFiles "src/utils" "packages/utils/src"
Move-GitFiles "src/llm" "packages/core/src/llm"
Move-GitFiles "src/rag" "packages/core/src/rag"
Move-GitFiles "src/memory" "packages/core/src/memory"

# Move tests
Write-Host "Moving tests..."
Move-GitFiles "src/tests" "apps/api/tests"
Move-GitFiles "tests" "apps/api/tests"

# Move configuration files
Write-Host "Moving configuration files..."
if (Test-Path "docker-compose.yml") {
    Copy-Item "docker-compose.yml" "infrastructure/docker/docker-compose.yml"
    git add "infrastructure/docker/docker-compose.yml"
    Remove-Item "docker-compose.yml"
}

Write-Host "Project reorganization complete!"
Write-Host "Please review the changes and commit them to git." 