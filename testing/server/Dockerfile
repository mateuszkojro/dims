# FROM python:3
FROM conda/miniconda3
COPY gif_server.py .
RUN apt update && apt install git -y
COPY dims-env.yml .
RUN conda env create -f dims-env.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "dims", "/bin/bash", "-c"]


RUN git clone https://github.com/mateuszkojro/dims
# RUN pip install dims/dimscommon
# CMD ["python", "gif_server.py"]
ENTRYPOINT ["conda", "run", "-n", "dims", "python", "gif_server.py"]
