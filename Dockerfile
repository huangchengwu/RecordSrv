FROM python:3.10.13-alpine3.18

# 🔥 添加这一行
USER root

WORKDIR /RecordSrv

# 暂时用官方源试试是否能成功
RUN apk update && \
    apk add --no-cache build-base dumb-init make && \
    pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY requirements.txt .
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

COPY . .

ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["sh", "-c", "make run"]
