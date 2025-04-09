FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y npm

COPY . .

WORKDIR /usr/src/app/lidoapp_bp/static
RUN npm init -y && npm install

WORKDIR /usr/src/app


CMD [ "python", "./app.py" ]
