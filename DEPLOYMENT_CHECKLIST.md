# Django Blog Deployment Checklist

This checklist is used when preparing the blog project for production deployment.

## 1. Local Final Checks

Run these commands before deployment:

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py runserver