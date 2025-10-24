#Use official Python image as base
FROM python:3.12-slim

#Set environment variables
ENV PYTHONWRITEBYTECODE=1
ENV PYTHONUMBUFFERED=1

#Set working directory
WORKDIR /app

#Copy the requirements first (for caching)
COPY requirements.txt .

#Install the dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN playwright install --with-deps

#Copy app folder, csv data is locally store for faster docker runs
#COPY app/ ./app

#Default command to run the script
CMD ["python", "app/main.py"]