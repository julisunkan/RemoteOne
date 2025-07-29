# Deploy WiFi File Server to Render

This guide will help you deploy your file server to Render, making it accessible from anywhere on the internet.

## Prerequisites

1. **GitHub Account**: You'll need to push your code to GitHub
2. **Render Account**: Sign up at [render.com](https://render.com) (free tier available)

## Deployment Steps

### 1. Prepare Your Repository

Make sure your project has these files:
- `render.yaml` - Render service configuration
- `render_requirements.txt` - Python dependencies
- `app.py` - Main Flask application
- `main.py` - Application entry point
- `templates/` - HTML templates
- `static/` - CSS, JS, and other static files

### 2. Push to GitHub

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Prepare for Render deployment"

# Add your GitHub repository as remote
git remote add origin https://github.com/yourusername/your-repo-name.git

# Push to GitHub
git push -u origin main
```

### 3. Deploy on Render

1. **Log in to Render**: Go to [render.com](https://render.com) and sign in
2. **Create New Service**: Click "New +" → "Web Service"
3. **Connect Repository**: 
   - Choose "Build and deploy from a Git repository"
   - Connect your GitHub account
   - Select your file server repository
4. **Configure Service**:
   - **Name**: `wifi-file-server` (or any name you prefer)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r render_requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 1 main:app`
5. **Environment Variables**: Render will automatically generate `SESSION_SECRET`
6. **Deploy**: Click "Create Web Service"

### 4. Alternative: Use render.yaml (Infrastructure as Code)

If you have the `render.yaml` file in your repository:

1. Go to Render Dashboard
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will automatically read the `render.yaml` configuration
5. Click "Apply" to deploy

## Configuration Details

### Environment Variables

Render automatically sets:
- `PORT` - The port your app should listen on
- `SESSION_SECRET` - Secure session key (auto-generated)

### File Storage

The configuration includes a persistent disk for file uploads:
- **Mount Path**: `/opt/render/project/src/uploads`
- **Size**: 1GB (can be increased in paid plans)
- **Persistence**: Files survive deployments and restarts

### Resource Limits

**Free Tier**:
- 512MB RAM
- Shared CPU
- 1GB persistent storage
- Service sleeps after 15 minutes of inactivity

**Paid Plans**: Higher resources and always-on service

## Post-Deployment

### Access Your Application

1. **Find Your URL**: After deployment, Render provides a URL like `https://wifi-file-server-abcd.onrender.com`
2. **First Visit**: The app will show the login page
3. **Password**: Check the Render logs for the generated password
4. **Login**: Use the password to access your file server

### View Logs

To see the server password and debug issues:
1. Go to your service in Render Dashboard
2. Click "Logs" tab
3. Look for: `Server initialized - URL: https://..., Password: ...`

### Custom Domain (Optional)

In paid plans, you can use your own domain:
1. Go to service settings
2. Add custom domain
3. Configure DNS records as instructed

## Security Considerations

### Production Security

1. **HTTPS**: Render automatically provides SSL certificates
2. **Session Secret**: Auto-generated secure key
3. **File Upload Limits**: 500MB per file (configurable)
4. **Password Protection**: Required for all access

### Network Access

- **Public Internet**: Accessible from anywhere (unlike local WiFi version)
- **No QR Code**: QR codes not needed since URL is accessible globally
- **Firewall**: No local firewall concerns

## Troubleshooting

### Common Issues

1. **Build Fails**: Check that `render_requirements.txt` has correct dependencies
2. **App Won't Start**: Verify `main.py` imports and runs correctly
3. **Files Not Persisting**: Ensure disk is properly mounted
4. **Password Not Showing**: Check logs in Render dashboard

### Debug Commands

View detailed logs:
```bash
# In Render dashboard, go to Logs tab
# Look for startup messages and any error traces
```

### Restart Service

If needed, restart from Render dashboard:
1. Go to your service
2. Click "Manual Deploy"
3. Choose "Clear build cache & deploy"

## Cost Considerations

### Free Tier
- Good for personal use and testing
- Service sleeps when inactive
- Limited resources

### Paid Plans
- Always-on service
- More storage and bandwidth
- Better performance
- Custom domains

## Differences from Local Version

### Cloud Deployment Changes
- Uses cloud-friendly URL detection
- Persistent disk storage instead of local folders
- Environment-based configuration
- HTTPS instead of HTTP
- Global accessibility instead of local network only

### Features Maintained
- Password authentication
- File upload/download
- Web interface
- All file type support
- Progressive Web App features

## Support

For deployment issues:
- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Render Support**: Available in dashboard
- **GitHub Issues**: Report bugs in your repository

Your file server will be accessible worldwide once deployed!