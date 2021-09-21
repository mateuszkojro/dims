FROM python:3
COPY ./ /tests
COPY ./ /tests/dimscommon
WORKDIR /tests
RUN pip install --no-cache-dir ./dimscommon
CMD ["python", "./dimscommon/test/test.py"]