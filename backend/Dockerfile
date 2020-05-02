# Use an official Python runtime as a parent image
FROM python:3.7

# Adding backend directory to make absolute filepaths consistent across services
WORKDIR /app/backend

# Install Python dependencies
COPY requirements.txt /app/backend
RUN pip install -r requirements.txt

# Add the rest of the code
COPY . /app/backend

# Make port 8000 available for the app
EXPOSE 8000

RUN mkdir staticfiles

# Collect staticfiles, such as the css & javascript from the default admin site
# which comes by default from django
RUN python3 manage.py collectstatic

# Create logging folder for gunicorn.
RUN mkdir -p /var/log/gunicorn

CMD python3 manage.py migrate && gunicorn tsg.wsgi:application \
    --bind 0.0.0.0:8000 \
    --error-logfile /var/log/gunicorn/error.log \
    --access-logfile /var/log/gunicorn/access.log
