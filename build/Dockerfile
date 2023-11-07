FROM ubuntu:22.04

# Set timezone
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install packages
RUN apt-get update
RUN apt install -y software-properties-common
RUN apt-get update

# For some reason apt really prefers python to be installed first
RUN apt install -y python3-dev
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN apt install -y git python3-pip neovim

# install python requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# add github args
#ENV GH_TOKEN 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
ARG GH_TOKEN

WORKDIR /app

# copy the files
COPY src src

ENTRYPOINT ["python"]
CMD ["src/search.py"]
