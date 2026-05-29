# PDF Toolkit Pro - Deploy to PythonAnywhere (100% Free)

## No Credit Card Required!

### Step 1: Create PythonAnywhere Account
1. Go to https://www.pythonanywhere.com
2. Click **"Pricing & signup"**
3. Choose **"Beginner"** (FREE) - no card needed!
4. Complete registration

### Step 2: Upload Your Code

**Option A: Clone from GitHub (Recommended)**

1. Open **Bash console** in PythonAnywhere
2. Run:
```bash
git clone https://github.com/bhanu646/pdf-toolkit.git
```

**Option B: Upload Files Manually**

1. In PythonAnywhere dashboard, go to **Files**
2. Create folder: `pdf-toolkit`
3. Upload these files:
   - `app.py`
   - `requirements.txt`
   - `templates/index.html`
   - `static/css/style.css`
   - `static/js/main.js`

### Step 3: Install Dependencies

In Bash console:
```bash
cd pdf-toolkit
pip install --user -r requirements.txt
```

### Step 4: Configure Web App

1. Go to **Web** tab
2. Click **"Add a new web app"**
3. Choose **"Manual configuration"**
4. Select **Python 3.11**
5. Click **Next**

### Step 5: Set Up WSGI File

1. Click on the WSGI configuration file link
2. Replace content with:

```python
import sys
path = '/home/YOUR_USERNAME/pdf-toolkit'
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application
```

**Replace `YOUR_USERNAME` with your PythonAnywhere username!**

3. Save and go back to Web tab

### Step 6: Configure Static Files

In Web tab, under "Static files":
- URL: `/static/` 
- Directory: `/home/YOUR_USERNAME/pdf-toolkit/static`

### Step 7: Reload Web App

Click the **Reload** button

### Step 8: Your Site is Live!

URL will be: `https://YOUR_USERNAME.pythonanywhere.com`

---

## Important Notes

- **File Storage**: PythonAnywhere has limited storage. Files are temporary!
- **No Persistent Storage**: Uploaded files are deleted after processing
- **For Production**: Consider upgrading for persistent storage

---

## Troubleshooting

**404 Errors?**
- Check static files path is correct
- Ensure WSGI file path is correct

**Import Errors?**
- Make sure all requirements installed: `pip install --user -r requirements.txt`

**App Not Loading?**
- Check Web tab for error logs
- Click "Reload" after any changes