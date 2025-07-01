# Use official Python base image
FROM python:3.12.3

# Set the working directory
WORKDIR /usr/src/app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Collect static files (optional for admin/css)
# RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run migrations automatically on startup (optional)
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

# # Or if you prefer without migrations:
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
