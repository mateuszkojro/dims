FROM python:3
COPY gif_server.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
CMD ['python', 'gif_server.py']