FROM alpine:3.13

RUN apk add python3 py3-pip3 && \
    pip3 install python-dotenv discord.py SQLAlchemy

COPY app /app
WORKDIR /app

CMD [ "python3", "bot.py" ]