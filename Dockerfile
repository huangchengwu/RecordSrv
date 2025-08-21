FROM python:3.11-slim
# 🔥 添加这一行
USER root

WORKDIR /RecordSrv

# 暂时用官方源试试是否能成功
RUN apt-get update && \
    apt-get install -y dumb-init ffmpeg make && \
    pip install --upgrade pip  

COPY requirements.txt .
RUN pip install -r requirements.txt  
COPY . .

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["sh", "-c", "make run & make celery"]
