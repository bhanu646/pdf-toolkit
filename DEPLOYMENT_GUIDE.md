# PDF Toolkit Pro - Deployment Steps

## Quick Deploy to Render (15 minutes)

### Step 1: Create GitHub Account
1. Go to https://github.com
2. Click "Sign Up"
3. Create username and password
4. Verify your email

### Step 2: Upload Project to GitHub
1. Go to https://github.com/new
2. Repository name: `pdf-toolkit-pro`
3. Select "Public"
4. Click "Create repository"
5. **Do NOT initialize with README**
6. Copy these commands and run in Git Bash:

```bash
cd "E:/Bhanu Gupta/SIH/pdf-toolkit"
git remote add origin https://github.com/YOUR_USERNAME/pdf-toolkit-pro.git
git push -u origin master
```
7. Enter your GitHub username and password when asked

### Step 3: Deploy to Render
1. Go to https://render.com
2. Click "Sign Up" → "Sign in with GitHub"
3. Authorize Render to access your GitHub
4. Click **"New +"** → **"Web Service"**
5. Find and select `pdf-toolkit-pro` repository
6. Fill in settings:
   - **Name**: `pdf-toolkit-pro`
   - **Region**: Singapore (or closest to you)
   - **Branch**: `master`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
7. Click **"Create Web Service"**
8. Wait 2-3 minutes for deployment

### Step 4: Your Site is Live!
- URL: `https://pdf-toolkit-pro.onrender.com`
- Share this URL with anyone!

---

## Add Custom Domain (Optional)

### In Render Dashboard:
1. Go to your deployed service
2. Click "Settings" tab
3. Scroll to "Custom Domains"
4. Add your domain (e.g., `pdf.example.com`)
5. Add the DNS records shown to your domain provider
6. Wait for SSL certificate (auto-provisioned)

---

## Files in This Project

```
pdf-toolkit/
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── render.yaml         # Render deployment config
├── static/
│   ├── css/style.css   # Styling
│   └── js/main.js      # Frontend logic
└── templates/
    └── index.html      # Main page
```

---

## Support

If you face issues:
- Render Docs: https://render.com/docs
- GitHub Help: https://docs.github.com