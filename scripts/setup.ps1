# Check for Chocolatey installation
if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
}

# Install required tools
Write-Host "Installing required tools..."
choco install -y git python nodejs docker-desktop vscode

# Install global npm packages
Write-Host "Installing global npm packages..."
npm install -g pnpm

# Setup Python virtual environment
Write-Host "Setting up Python environment..."
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r apps/api/requirements.txt

# Install Node.js dependencies
Write-Host "Installing Node.js dependencies..."
pnpm install

# Setup git config
Write-Host "Setting up git configuration..."
git config core.autocrlf true
git config --global init.defaultBranch main

Write-Host "Setup complete! Please restart your computer to ensure Docker works correctly." 