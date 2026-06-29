# FoodExpress - Fixed Django Project

## What was fixed

- Added safe local defaults in `mysite/settings.py`.
- Project now runs with SQLite by default, so MySQL is not required for local testing.
- Cloudinary is optional. Local media storage is used unless `USE_CLOUDINARY=True`.
- Fixed static/media settings for local development.
- Added `.env.example` without private credentials.
- Added demo seed command: `python manage.py seed_demo`.
- Verified these pages return successfully: home, restaurants, food list, food detail, cart, login, register.

## How to run

```bash
cd backend
python -m venv env

# Windows
.\env\Scripts\activate

# macOS/Linux
source env/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Admin login after seed:

```text
username: admin
password: admin12345
```

## Use MySQL instead of SQLite

Edit `.env`:

```env
DB_ENGINE=django.db.backends.mysql
DB_NAME=restaurant_app_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

Then create the database in MySQL and run:

```bash
python manage.py migrate
python manage.py seed_demo
```

## Use Cloudinary

Edit `.env`:

```env
USE_CLOUDINARY=True
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

## Razorpay payments

Add these values to your `.env` for live payments:

```env
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

If these values are not set, the app uses a local demo payment flow so checkout can still be tested in development.
