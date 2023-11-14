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

#RUN java -jar /opt/LFH_FHIR/fhir-server-dist/tools/fhir-persistence-schema-5.1.1-cli.jar --prop "db.create=Y" --prop "db.database=/opt/LFH_FHIR/derby_fhirDB" --db-type derby

ENTRYPOINT ["/opt/LFH_FHIR/wlp/bin/server", "run"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]
# curl -k -u 'fhiruser:test' 'https://localhost:9443/fhir-server/api/v4/$healthcheck'
