version ?= 0.0.1
p ?= 80

install:
	python -m pip install -r requirements.txt  -i https://mirrors.aliyun.com/pypi/simple/ 
run:
	python manage.py runserver 0.0.0.0:$(p)
up:
	python manage.py makemigrations 
	python manage.py  migrate
pip:
	python -m pip install -r requirements.txt  -i https://mirrors.aliyun.com/pypi/simple/ 
dev:
	cp -rf RecordSrv/settings.py_dev  RecordSrv/settings.py
prd:
	cp -rf RecordSrv/settings.py_prd RecordSrv/settings.py
build:
	docker build -t recordsrv:$(version) .
cp_local:
	# 打包项目
	rm -rf RecordSrv.tar.gz
	tar cvf RecordSrv.tar.gz ~/RecordSrv
	scp -r RecordSrv.tar.gz root@192.168.100.44:/tmp
	ssh root@192.168.100.44 "cd /tmp && tar xvf RecordSrv.tar.gz && cd /tmp/Users/mac-512/RecordSrv && make build"
