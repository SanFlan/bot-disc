FROM python:3-slim-buster

RUN pip3 install python-dotenv discord.py SQLAlchemy

COPY app /app
WORKDIR /app

CMD [ "python3", "bot.py" ]