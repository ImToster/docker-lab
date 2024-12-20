FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt --no-cache && \
    rm -rf /var/cache/apk/* && \
    rm -rf /root/.cache/pip

COPY . .
RUN chmod -R 777 /app

EXPOSE 3000

RUN adduser --disabled-password appuser
USER appuser

ENTRYPOINT [ "./entrypoint.sh" ]