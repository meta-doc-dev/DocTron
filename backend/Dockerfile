FROM python:3.11
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Change the working directory to the cloned repository
WORKDIR /code/grobid_client_python

# Run the setup.py script
WORKDIR /code
COPY . /code/
