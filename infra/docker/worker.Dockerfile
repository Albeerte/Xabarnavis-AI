FROM python:3.11-slim

WORKDIR /app
COPY apps/api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY apps/api ./apps/api
CMD ["python", "-c", "print('Xabarnavis worker placeholder')"]
