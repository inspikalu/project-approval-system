# Flask Secret Key Configuration

## Security Fix Applied

The hardcoded Flask secret key has been removed to fix the security vulnerability **python:S6779**.

## How to Set Up

### Option 1: Environment Variable (Recommended for Production)

1. Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

2. Set the environment variable before running the app:
```bash
export SECRET_KEY='your_generated_key_here'
python app.py
```

### Option 2: Using .env File

1. Create a `.env` file (already in `.gitignore`):
```bash
cp .env.example .env
```

2. Generate and add your secret key to `.env`:
```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env
```

3. Install python-dotenv:
```bash
pip install python-dotenv
```

4. Load it in your app (optional - the app will auto-generate if not set):
```python
from dotenv import load_dotenv
load_dotenv()
```

### Option 3: Auto-Generated (Development Only)

If no `SECRET_KEY` is set, the app will automatically generate a secure random key at startup. 

**⚠️ WARNING:** This is only suitable for development. Sessions will be invalidated on each restart.

## What Changed

**Before (Insecure):**
```python
app.secret_key = 'super_secret_key_for_session'
```

**After (Secure):**
```python
app.secret_key = os.environ.get('SECRET_KEY')
if not app.secret_key:
    app.secret_key = secrets.token_hex(32)
    print("WARNING: Using auto-generated secret key...")
```

## Why This Matters

- **Prevents session hijacking**: Secret keys sign session cookies
- **Keeps secrets out of version control**: Environment variables aren't committed
- **Uses cryptographically secure values**: `secrets.token_hex()` generates random keys
- **Complies with security best practices**: Fixes SonarQube rule python:S6779
