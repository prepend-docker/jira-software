FROM adoptopenjdk/openjdk8:slim

ENV RUN_USER							jira
ENV RUN_GROUP							jira
ENV RUN_UID							2001
ENV RUN_GID							2001

# https://confluence.atlassian.com/display/JSERVERM/Important+directories+and+files
ENV JIRA_HOME          						/var/atlassian/application-data/jira
ENV JIRA_INSTALL_DIR   						/opt/atlassian/jira

WORKDIR $JIRA_HOME

# Expose HTTP port
EXPOSE 8080
EXPOSE 3801

CMD ["/entrypoint.py", "-fg"]
ENTRYPOINT ["/tini", "--"]

RUN apt-get update \
	&& apt-get install -y --no-install-recommends wget fontconfig python3 python3-jinja2 \
        && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
        && dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install \
	&& apt-get clean autoclean && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

ARG TINI_VERSION=v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini

ARG JIRA_VERSION
ARG ARTEFACT_NAME=atlassian-jira-software
#ARG DOWNLOAD_URL=https://product-downloads.atlassian.com/software/jira/downloads/${ARTEFACT_NAME}-${JIRA_VERSION}.tar.gz
ARG DOWNLOAD_URL=https://www.atlassian.com/software/jira/downloads/binary/atlassian-jira-software-8.5.2.tar.gz
RUN groupadd --gid ${RUN_GID} ${RUN_GROUP} \
    && useradd --uid ${RUN_UID} --gid ${RUN_GID} --home-dir ${JIRA_HOME} --shell /bin/bash ${RUN_USER} \
    && echo PATH=$PATH > /etc/environment \
    \
    && mkdir -p                             ${JIRA_INSTALL_DIR} \
    && curl -L --silent                  ${DOWNLOAD_URL} | tar -xz --strip-components=1 -C "${JIRA_INSTALL_DIR}" \
    && chmod -R "u=rwX,g=rX,o=rX"        ${JIRA_INSTALL_DIR}/ \
    && chown -R root.                    ${JIRA_INSTALL_DIR}/ \
    && chown -R ${RUN_USER}:${RUN_GROUP} ${JIRA_INSTALL_DIR}/logs \
    && chown -R ${RUN_USER}:${RUN_GROUP} ${JIRA_INSTALL_DIR}/temp \
    && chown -R ${RUN_USER}:${RUN_GROUP} ${JIRA_INSTALL_DIR}/work \
    \
    && sed -i -e 's/^JVM_SUPPORT_RECOMMENDED_ARGS=""$/: \${JVM_SUPPORT_RECOMMENDED_ARGS:=""}/g' ${JIRA_INSTALL_DIR}/bin/setenv.sh \
    && sed -i -e 's/^JVM_\(.*\)_MEMORY="\(.*\)"$/: \${JVM_\1_MEMORY:=\2}/g' ${JIRA_INSTALL_DIR}/bin/setenv.sh \
    \
    && touch /etc/container_id && chown  ${RUN_USER}:${RUN_GROUP} /etc/container_id \
    && chown -R ${RUN_USER}:${RUN_GROUP} ${JIRA_HOME}

VOLUME ["${JIRA_HOME}"] # Must be declared after setting perms

COPY entrypoint.py					/entrypoint.py
COPY config/*						/opt/atlassian/etc/
