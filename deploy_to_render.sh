#!/bin/bash
# Deploy WiFi File Server to Render

echo "=== Render Deployment Helper ==="
echo

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    echo "✓ Git repository initialized"
fi

# Add all files
echo "Adding files to git..."
git add .
echo "✓ Files added"

# Create commit
echo "Creating commit..."
git commit -m "Prepare for Render deployment - $(date)"
echo "✓ Commit created"

echo
echo "✓ Repository prepared for deployment!"
echo
echo "Next steps:"
echo "1. Push to GitHub:"
echo "   git remote add origin https://github.com/yourusername/your-repo.git"
echo "   git push -u origin main"
echo
echo "2. Deploy on Render:"
echo "   - Go to render.com"
echo "   - Create new Web Service"
echo "   - Connect your GitHub repository"
echo "   - Use the settings from render.yaml"
echo
echo "3. Find your deployment URL in Render dashboard"
echo "4. Check logs for the generated password"
echo
echo "Files ready for deployment:"
echo "  ✓ render.yaml - Render configuration"
echo "  ✓ render_requirements.txt - Dependencies"
echo "  ✓ Procfile - Alternative start command"
echo "  ✓ RENDER_DEPLOYMENT.md - Detailed guide"
echo
echo "Your file server will be accessible worldwide once deployed!"