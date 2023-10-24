FROM ubuntu:22.04
ARG DEBIAN_FRONTEND=noninteractive
EXPOSE 80
RUN apt-get update \ 
	&& apt-get upgrade -y \ 
	&& apt-get install wget libglib2.0-0 libgssapi-krb5-2 libglu1-mesa-dev libpulse-mainloop-glib0 python3-pip apache2 systemctl git -y \
	&& rm -rf /var/lib/apt/lists/* \
	&& a2dismod mpm_event \
	&& a2enmod mpm_worker \
	&& service apache2 stop \
	&& systemctl start apache2 \
	&& mkdir -p /var/www/html/site \
	&& mkdir -p /home/MLP/FRVelneo/Scripts \
	&& pip install pipenv
COPY app.conf /etc/apache2/sites-available
COPY getName.py /home/MLP/FRVelneo/Scripts
COPY registerUser.py /home/MLP/FRVelneo/Scripts
COPY app.py /var/www/html/site
COPY app.wsgi /var/www/html/site
COPY Pipfile /temp
CMD sleep infinity 
