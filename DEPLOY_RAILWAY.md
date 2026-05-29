# PDF Toolkit Pro - Deploy to Railway (Free)

## Prerequisites
1. GitHub account with the `pdf-toolkit` project pushed
2. Railway account (sign up at railway.app with GitHub)

## Deploy Steps

### Step 1: Push Code to GitHub

1. Go to https://github.com and create a new repository named `pdf-toolkit`
2. Run these commands in Git Bash:

```bash
cd "E:/Bhanu Gupta/SIH/pdf-toolkit"

# Initialize git if not already
git init
git add .
git commit -m "Initial commit - PDF Toolkit Pro"

# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/pdf-toolkit.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy to Railway

1. Go to https://railway.app and click **"Login"** → **"Login with GitHub"**
2. Authorize Railway to access your GitHub repositories
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select the `pdf-toolkit` repository
5. Railway will auto-detect Python and deploy

### Step 3: Configure Environment

1. In Railway dashboard, go to your deployment
2. Click **"Variables"** tab
3. Add: `PORT` = `8000`
4. Railway will assign a URL like: `https://pdf-toolkit.up.railway.app`

### Step 4: Wait for Deployment

- Takes 2-5 minutes
- Check "Logs" tab for progress
- Your site will be live at the Railway URL!

---

## Custom Domain Setup (Optional)

### In Railway:
1. Go to your project → Settings → Domains
2. Click **"Add Domain"**
3. Enter your domain (e.g., `pdf.yoursite.com`)
4. Railway will show DNS records to add

### At Your Domain Provider:
Add these DNS records:
- Type: `CNAME`
- Name: `pdf` (or subdomain you chose)
- Value: `lb.railway.app`

Wait 5-10 minutes for DNS propagation, then your domain will work!

---

## Project Files
```
pdf-toolkit/
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── railway.json        # Railway deployment config
├── static/
│   ├── css/style.css
│   └── js/main.js
└── templates/
    └── index.html
```

## Troubleshooting

**Build fails?**
- Check that requirements.txt is in root
- Ensure all dependencies are listed

**Server error?**
- Check Railway logs for error details
- Verify PORT environment variable is set

**502 Error?**
- Start command should be: `gunicorn app:app --bind 0.0.0.0:$PORT`