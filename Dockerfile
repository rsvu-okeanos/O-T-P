# node/python/beursborrel
# VERSION 0.1

FROM ubuntu:16.04
MAINTAINER Floris Hoogenboom <floris@digitaldreamworks.nl>

# Get some security updates
RUN apt-get update
RUN apt-get -y upgrade

#Instal necesarry system packages
RUN apt-get -y install curl
RUN apt-get -y install apt-utils

# Install python, node and npm
RUN apt-get -y install python3 python3-pip python3-dev build-essential
RUN apt-get -y install libssl-dev libffi-dev
RUN pip3 install --upgrade pip
RUN curl -sL https://deb.nodesource.com/setup_6.x | bash -
RUN apt-get -y install nodejs
RUN apt-get -y install php7.0
RUN apt-get -y install php7.0-mcrypt
RUN apt-get -y install supervisor

# Add our application
ADD app /usr/local/app
ADD conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN pip3 install -r /usr/local/app/requirements.txt

EXPOSE 3000
EXPOSE 80

CMD ["/usr/bin/supervisord"]
