# Background Remover Python Application

A simple flask app to remove the background of an image with [Rembg](https://github.com/danielgatis/rembg)

## Run it locally:

```
pip install -r requirements.txt
python app.py
```

## Building Docker Image:

```
docker build -t flask-rmbg-app .
```

## Running Docker Image:

```
docker run -p 5100:5100 flask-rmbg-app
```
