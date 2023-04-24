FROM continuumio/miniconda3:latest

COPY . /military_qa

WORKDIR /military_qa

RUN apt-get update \
    && apt-get upgrade \
    && apt-get -y install build-essential \
    && apt-get -y install g++ \
    && apt-get -y install gcc

RUN conda create -n chatgpt python=3.8 \
    && conda activate chatgpt \
    && pip install -r requirements.txt --default-timeout=1000 -i https://pypi.tuna.tsinghua.edu.cn/simple

EXPOSE 15001 15002

VOLUME /military_qa/data
VOLUME /military_qa/database

CMD ["python", "documents_qa_api.py"]