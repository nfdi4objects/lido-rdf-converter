FROM python:3.12-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y npm libxml2-utils

COPY . .
RUN chmod +x ./lido2rdf
RUN chmod +x ./lido2rdf.py
WORKDIR /app/lidoapp_bp/static
RUN npm init -y && npm install

WORKDIR /app


# Allow to directly call scripts in the base directory
ENV PATH="/app:$PATH"
CMD [ "python", "./app.py" ]
