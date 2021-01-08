FROM python:3.9

RUN mkdir /app

WORKDIR /app

ADD . /app

RUN pip install -U pip
RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8000


# CMD ["echo", "-e", "[TOKEN]\ntoken=Botのシークレットトークン", ">", "config.ini", "&&", "python", "main.py"]
# CMD ["python", "main.py"]