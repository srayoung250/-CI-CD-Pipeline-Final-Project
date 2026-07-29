# Mechanic API CI/CD Deployment Guide

## Step 1: Create Render PostgreSQL Database

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **PostgreSQL**
3. Fill in the database details:
   - Name: `mechanic-shop-db`
   - Database: `mechanic_shop`
   - User: `mechanic_user`
   - Region: Choose closest to you
4. Click **Create Database**
5. Once created, copy the **External Database URL** (looks like: `postgresql://user:password@host:5432/db`)
6. Save this for later - you'll need it for environment variables

## Step 2: Deploy Flask App to Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository:
   - Select your GitHub account
   - Choose the repository: `-CI-CD-Pipeline-Final-Project`
   - Click **Connect**
4. Fill in the Web Service details:
   - Name: `mechanic-shop-api`
   - Environment: `Python 3`
   - Region: Same as your database
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn flask_app:app`
5. Click **Advanced** and set Environment Variables:
   ```
   FLASK_ENV = production
   DATABASE_URI = postgresql://user:password@host:5432/mechanic_shop
   SECRET_KEY = your-secure-random-key-here
   ```
   (Replace with your actual database URL and generate a strong secret key)
6. Click **Create Web Service**
7. Wait for deployment to complete

## Step 3: Get Render Service ID and API Key

1. From the Render dashboard, go to your service
2. In the URL bar, note your **Service ID** (looks like: `srv_xxxxxxxxxxxxx`)
3. Go to Account Settings → API Keys
4. Click **Create API Key** and copy it (save securely)

## Step 4: Add GitHub Secrets

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click **New repository secret**
4. Add two secrets:
   - Name: `RENDER_SERVICE_ID` → Value: (your service ID)
   - Name: `RENDER_API_KEY` → Value: (your API key)

## Step 5: Update Swagger Documentation

After successful deployment:

1. Your live API URL will be something like: `mechanic-shop-api.onrender.com`
2. Edit `app/swagger_definitions.py`
3. Update the swagger template:
   ```python
   "host": "mechanic-shop-api.onrender.com",  # Remove https:// and any paths
   "schemes": ["https"],  # Change from ["http", "https"] to just ["https"]
   ```
4. Commit and push:
   ```bash
   git add app/swagger_definitions.py
   git commit -m "Update swagger host for production"
   git push
   ```

## Step 6: Verify CI/CD Pipeline

1. Go to your GitHub repository
2. Click **Actions** tab
3. You should see your workflow running
4. Monitor the build, test, and deploy jobs
5. Once complete, visit your live API: `https://mechanic-shop-api.onrender.com/apidocs`

## Testing Your Deployment

```bash
# Test your API (replace with your Render URL)
curl https://mechanic-shop-api.onrender.com/customers

# View logs on Render
# Dashboard → Your Service → Logs
```

## Troubleshooting

**Database connection error:**
- Verify DATABASE_URI environment variable is correct
- Check that Render database is running

**Build fails:**
- Check build logs in Render dashboard
- Ensure all dependencies in requirements.txt are compatible

**Tests fail in CI/CD:**
- Run tests locally: `pytest tests/ -v`
- Check test database configuration in `tests/base.py`

## Notes

- The `.env` file is for local development only (git ignored)
- Production environment variables are set in Render dashboard
- GitHub Actions will automatically deploy on push to main
