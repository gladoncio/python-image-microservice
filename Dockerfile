FROM python:3.10-alpine

WORKDIR /app

RUN apk add --no-cache \
    fontconfig \
    ttf-dejavu \
    ttf-freefont \
    ttf-liberation \
    font-noto

COPY app/requirements.txt .
RUN pip install -r requirements.txt

COPY app .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "app.py"]
