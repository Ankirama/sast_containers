FROM alpine:latest

RUN apk add --no-cache curl git php7 php7-pear php7-mbstring php7-dom php7-xmlrpc php7-soap php7-gd php7-xml php7-cli php7-zip php7-json php7-phar php7-openssl php7-curl php7-curl php7-iconv php7-tokenizer php7-xmlwriter php7-simplexml unzip python3

ADD https://getcomposer.org/download/1.10.17/composer.phar /opt/composer.phar

RUN git clone https://github.com/FloeDesignTechnologies/phpcs-security-audit.git /opt/phpcs_security

RUN php /opt/composer.phar install -d /opt/phpcs_security --no-dev
COPY base_ruleset.xml /opt/phpcs_security/base_ruleset.xml
COPY phpcs.py /bin/phpcs
RUN chmod +x /bin/phpcs

RUN mkdir /opt/data
VOLUME /opt/data
