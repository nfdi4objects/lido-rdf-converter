FROM python:3

WORKDIR /usr/src/app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Allow to directly call scripts in the base directory
ENV PATH="/app:$PATH"

# Start web client by default
CMD [ "python", "./app.py" ]
