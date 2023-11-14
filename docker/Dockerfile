FROM ubuntu:22.04

RUN yes |unminimize
RUN apt-get update
RUN apt-get install -y build-essential curl default-jre iputils-ping less man net-tools unzip vim wget

COPY files/.bashrc /root/.bashrc

RUN mkdir /opt/LFH_FHIR
RUN wget -O /opt/LFH_FHIR/fhir-install-5.1.1.zip https://github.com/LinuxForHealth/FHIR/releases/download/5.1.1/fhir-install-5.1.1.zip
WORKDIR /opt/LFH_FHIR
RUN unzip fhir-install-5.1.1.zip
RUN /opt/LFH_FHIR/fhir-server-dist/install.sh /opt/LFH_FHIR
COPY files/server.xml /opt/LFH_FHIR/wlp/usr/servers/defaultServer
COPY files/fhir-server-config-postgresql.json /opt/LFH_FHIR/wlp/usr/servers/defaultServer/config/default/fhir-server-config.json
COPY files/datasource-postgresql.xml /opt/LFH_FHIR/wlp/usr/servers/defaultServer/configDropins/defaults/datasource.xml

ENTRYPOINT ["/opt/LFH_FHIR/wlp/bin/server", "run"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]
# curl -k -u 'fhiruser:test' 'https://localhost:9443/fhir-server/api/v4/$healthcheck'
