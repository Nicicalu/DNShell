FROM python:3.7-alpine
WORKDIR /code
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5353
CMD ["python3", "control.py"]