![Atlassian Jira Software](https://wac-cdn.atlassian.com/dam/jcr:826c97dc-1f5c-4955-bfcc-ea17d6b0c095/jira%20software-icon-gradient-blue.svg?cdnVersion=492)![Atlassian Jira Service Desk](https://wac-cdn.atlassian.com/dam/jcr:8e0905be-0ee7-4652-ba3a-4e3db1143969/jira%20service%20desk-icon-gradient-blue.svg?cdnVersion=492)![Atlassian Jira Core](https://wac-cdn.atlassian.com/dam/jcr:f89f1ce5-60f1-47c2-b9f5-657de4940d31/jira%20core-icon-gradient-blue.svg?cdnVersion=492)

Jira Software is a software development tool used by agile teams.

* Check out [atlassian/jira-software](http://hub.docker.com/r/atlassian/jira-software/) on Docker Hub
* Learn more about Jira Software: [https://www.atlassian.com/software/jira](https://www.atlassian.com/software/jira)

Jira Service Desk is a fully featured service desk tool used by modern IT teams.

* Check out [atlassian/jira-servicedesk](http://hub.docker.com/r/atlassian/jira-servicedesk/) on Docker Hub
* Learn more about JIRA Service Desk: [https://www.atlassian.com/software/jira/service-desk](https://www.atlassian.com/software/jira/service-desk)

Jira Core is a project and task management solution built for business teams.

* Check out [atlassian/jira-core](http://hub.docker.com/r/atlassian/jira-core/) on Docker Hub
* Learn more about JIRA Core: [https://www.atlassian.com/software/jira/core](https://www.atlassian.com/software/jira/core)

# Contents

[TOC]

# Overview

This Docker container makes it easy to get an instance of Jira Software, Service Desk or Core up and running.

Note: Jira Software will be referenced in the examples provided.

# Quick Start

For the `JIRA_HOME` directory that is used to store application data (amongst
other things) we recommend mounting a host directory as a [data
volume](https://docs.docker.com/engine/tutorials/dockervolumes/#/data-volumes),
or via a named volume if using a docker version >= 1.9.

Additionally, if running Jira in Data Center mode it is required that a shared
filesystem is mounted. The mountpoint (inside the container) can be configured
with `JIRA_SHARED_HOME`.

To get started you can use a data volume, or named volumes. In this example
we'll use named volumes.

    docker volume create --name jiraVolume
    docker run -v jiraVolume:/var/atlassian/application-data/jira --name="jira" -d -p 8080:8080 atlassian/jira-software


**Success**. Jira is now available on [http://localhost:8080](http://localhost:8080)*

Please ensure your container has the necessary resources allocated to it. We
recommend 2GiB of memory allocated to accommodate the application server. See
[System Requirements](https://confluence.atlassian.com/adminjiraserver071/jira-applications-installation-requirements-802592164.html)
for further information.


_* Note: If you are using `docker-machine` on Mac OS X, please use `open
http://$(docker-machine ip default):8080` instead._

# Configuring Jira

This Docker image is intended to be configured from its environment; the
provided information is used to generate the application configuration files
from templates. This allows containers to be repeatably created and destroyed
on-the-fly, as required in advanced cluster configurations. Most aspects of the
deployment can be configured in this manner; the necessary environment variables
are documented below. However, if your particular deployment scenario is not
covered by these settings, it is possible to override the provided templates
with your own; see the section _Advanced Configuration_ below.

## Memory / Heap Size

If you need to override Jira's default memory allocation, you can control the minimum heap (Xms) and maximum heap (Xmx) via the below environment variables.

* `JVM_MINIMUM_MEMORY` (default: 384m)

   The minimum heap size of the JVM

* `JVM_MAXIMUM_MEMORY` (default: 768m)

   The maximum heap size of the JVM

## Reverse Proxy Settings

If Jira is run behind a reverse proxy server (e.g. a load-balancer or nginx server) as
[described here](https://confluence.atlassian.com/adminjiraserver072/integrating-jira-with-apache-using-ssl-828788158.html),
then you need to specify extra options to make Jira aware of the setup. They can
be controlled via the below environment variables.

* `ATL_PROXY_NAME` (default: NONE)

   The reverse proxy's fully qualified hostname. `CATALINA_CONNECTOR_PROXYNAME`
   is also supported for backwards compatability.

* `ATL_PROXY_PORT` (default: NONE)

   The reverse proxy's port number via which Jira is
   accessed. `CATALINA_CONNECTOR_PROXYPORT` is also supported for backwards
   compatability.

* `ATL_TOMCAT_PORT` (default: 8080)

   The port for Tomcat/Jira to listen on. Depending on your container
   deployment method this port may need to be
   [exposed and published][docker-expose].

* `ATL_TOMCAT_SCHEME` (default: http)

   The protocol via which Jira is accessed. `CATALINA_CONNECTOR_SCHEME` is also
   supported for backwards compatability.

* `ATL_TOMCAT_SECURE` (default: false)

   Set 'true' if `ATL_TOMCAT_SCHEME` is 'https'. `CATALINA_CONNECTOR_SECURE` is
   also supported for backwards compatability.

* `ATL_TOMCAT_CONTEXTPATH` (default: NONE)

   The context path the application is served over. `CATALINA_CONTEXT_PATH` is
   also supported for backwards compatability.

The following Tomcat/Catalina options are also supported. For more information,
see https://tomcat.apache.org/tomcat-7.0-doc/config/index.html.

* `ATL_TOMCAT_MGMT_PORT` (default: 8005)
* `ATL_TOMCAT_MAXTHREADS` (default: 100)
* `ATL_TOMCAT_MINSPARETHREADS` (default: 10)
* `ATL_TOMCAT_CONNECTIONTIMEOUT` (default: 20000)
* `ATL_TOMCAT_ENABLELOOKUPS` (default: false)
* `ATL_TOMCAT_PROTOCOL` (default: HTTP/1.1)
* `ATL_TOMCAT_ACCEPTCOUNT` (default: 10)

## JVM configuration

If you need to pass additional JVM arguments to Jira, such as specifying a custom trust store, you can add them via the below environment variable

* `JVM_SUPPORT_RECOMMENDED_ARGS`

   Additional JVM arguments for Jira

Example:

    docker run -e JVM_SUPPORT_RECOMMENDED_ARGS=-Djavax.net.ssl.trustStore=/var/atlassian/application-data/jira/cacerts -v jiraVolume:/var/atlassian/application-data/jira --name="jira" -d -p 8080:8080 atlassian/jira-software

## Database configuration

It is optionally possible to configure the database from the environment,
avoiding the need to do so through the web startup screen.

The following variables are all must all be supplied if using this feature:

* `ATL_JDBC_URL`

   The database URL; this is database-specific.

* `ATL_JDBC_USER`

   The database user to connect as.

* `ATL_JDBC_PASSWORD`

   The password for the database user.

* `ATL_DB_DRIVER`

   The JDBC driver class; supported drivers are:

   * `com.microsoft.sqlserver.jdbc.SQLServerDriver`
   * `com.mysql.jdbc.Driver`
   * `oracle.jdbc.OracleDriver`
   * `org.postgresql.Driver`

   The driver must match the DB type (see next entry).

* `ATL_DB_TYPE`

   The type of database; valid supported values are:

   * `mssql`
   * `mysql`
   * `oracle10g`
   * `postgres72`

Note: Due to licensing restrictions Jira does not ship with a MySQL or
Oracle JDBC drivers. To use these databases you will need to copy a suitable
driver into the container and restart it. For example, to copy the MySQL driver
into a container named "jira", you would do the following:

    docker cp mysql-connector-java.x.y.z.jar jira:/opt/atlassian/jira/lib
    docker restart jira

For more information see the page 
[Startup check: JIRA database driver missing](https://confluence.atlassian.com/jirakb/startup-check-jira-database-driver-missing-873872169.html).

### Optional database settings

The following variables are for the Tomcat JDBC connection pool, and are
optional. For more information on these see: https://tomcat.apache.org/tomcat-7.0-doc/jdbc-pool.html

* `ATL_DB_MAXIDLE` (default: 20)
* `ATL_DB_MAXWAITMILLIS` (default: 30000)
* `ATL_DB_MINEVICTABLEIDLETIMEMILLIS` (default: 5000)
* `ATL_DB_MINIDLE` (default: 10)
* `ATL_DB_POOLMAXSIZE` (default: 100)
* `ATL_DB_POOLMINSIZE` (default: 20)
* `ATL_DB_REMOVEABANDONED` (default: true)
* `ATL_DB_REMOVEABANDONEDTIMEOUT` (default: 300)
* `ATL_DB_TESTONBORROW` (default: false)
* `ATL_DB_TESTWHILEIDLE` (default: true)
* `ATL_DB_TIMEBETWEENEVICTIONRUNSMILLIS` (default: 30000)


## Data Center configuration

This docker image can be run as part of a
[Data Center](https://confluence.atlassian.com/enterprise/jira-data-center-472219731.html)
cluster. You can specify the following properties to start Jira as a Data Center
node, instead of manually configuring a cluster.properties file, See
[Installing Jira Data Center](https://confluence.atlassian.com/adminjiraserver071/installing-jira-data-center-802592197.html)
for more information on each property and its possible configuration.

### Cluster configuration

*Jira Software and Jira Service Desk only*

* `CLUSTERED` (default: false)

   Set 'true' to enable clustering configuration to be used. This will create a
   `cluster.properties` file inside the container's `$JIRA_HOME` directory.

* `JIRA_NODE_ID` (default: jira_node_<container-id>)

   The unique ID for the node. By default, this includes a randomly generated ID
   unique to each container, but can be overridden with a custom value.

* `JIRA_SHARED_HOME` (default: $JIRA_HOME/shared)

   The location of the shared home directory for all Jira nodes. **Note**: This
   must be real shared filesystem that is mounted inside the
   container. Additionally, see the note about UIDs.

* `EHCACHE_PEER_DISCOVERY` (default: default)

   Describes how nodes find each other.

* `EHCACHE_LISTENER_HOSTNAME` (default: NONE)

   The hostname of the current node for cache communication. Jira Data Center
   will resolve this this internally if the parameter isn't set.

* `EHCACHE_LISTENER_PORT` (default: 40001)

   The port the node is going to be listening to. Depending on your container
   deployment method this port may need to be [exposed and published][docker-expose].

* `EHCACHE_OBJECT_PORT` (default: dynamic)

   The port number on which the remote objects bound in the registry receive
   calls. This defaults to a free port if not specified. This port may need to
   be [exposed and published][docker-expose].

* `EHCACHE_LISTENER_SOCKETTIMEOUTMILLIS` (default: 2000)

   The default timeout for the Ehcache listener.

* `EHCACHE_MULTICAST_ADDRESS` (default: NONE)

   A valid multicast group address. Required when EHCACHE_PEER_DISCOVERY is set
   to 'automatic' instead of 'default'.

* `EHCACHE_MULTICAST_PORT` (default: NONE)

   The dedicated port for the multicast heartbeat traffic. Required when
   EHCACHE_PEER_DISCOVERY is set to 'automatic' instead of 'default'.  Depending
   on your container deployment method this port may need to be
   [exposed and published][docker-expose].

* `EHCACHE_MULTICAST_TIMETOLIVE` (default: NONE)

   A value between 0 and 255 which determines how far the packets will
   propagate. Required when EHCACHE_PEER_DISCOVERY is set to 'automatic' instead
   of 'default'.

* `EHCACHE_MULTICAST_HOSTNAME` (default: NONE)

   The hostname or IP of the interface to be used for sending and receiving
   multicast packets. Required when EHCACHE_PEER_DISCOVERY is set to 'automatic'
   instead of 'default'.

### Shared directory and user IDs

By default the Jira application runs as the user `jira`, with a UID and GID
of 2001. Consequently this UID must have write access to the shared
filesystem. If for some reason a different UID must be used, there are a number
of options available:

* The Docker image can be rebuilt with a different UID.
* Under Linux, the UID can be remapped using
  [user namespace remapping](https://docs.docker.com/engine/security/userns-remap/).

To preserve strict permissions for certain configuration files, this container starts as
`root` to perform bootstrapping before running Jira under a non-privileged user account.
If you wish to start the container as a non-root user, please note that Tomcat
configuration will be skipped and a warning will be logged. You may still apply custom
configuration in this situation by mounting a custom server.xml file directly to
`/opt/atlassian/jira/conf/server.xml`

Database and Clustering bootstrapping will work as expected when starting this container
as a non-root user.

## Advanced Configuration

As mentioned at the top of this section, the settings from the environment are
used to populate the application configuration on the container startup. However
in some cases you may wish to customise the settings in ways that are not
supported by the environment variables above. In this case, it is possible to
modify the base templates to add your own configuration. There are three main
ways of doing this; modify our repository to your own image, build a new image
from the existing one, or provide new templates at startup. We will briefly
outline this methods here, but in practice how you do this will depend on your
needs.

#### Building your own image

* Clone the Atlassian repository at https://bitbucket.org/atlassian-docker/docker-atlassian-jira/
* Modify or replace the [Jinja](https://jinja.palletsprojects.com/) templates
  under `config`; _NOTE_: The files must have the `.j2` extensions. However you
  don't have to use template variables if you don't wish.
* Build the new image with e.g: `docker build --tag my-jira-8-image --build-arg JIRA_VERSION=8.x.x .`
* Optionally push to a registry, and deploy.

#### Build a new image from the existing one

* Create a new `Dockerfile`, which starts with the line e.g: `FROM
  atlassian/jira-software:latest`.
* Use a `COPY` line to overwrite the provided templates.
* Build, push and deploy the new image as above.

#### Overwrite the templates at runtime

There are two main ways of doing this:

* If your container is going to be long-lived, you can create it, modify the
  installed templates under `/opt/atlassian/etc/`, and then run it.
* Alternatively, you can create a volume containing your alternative templates,
  and mount it over the provided templates at runtime
  with `--volume my-config:/opt/atlassian/etc/`.

# Logging

By default the Jira logs are written inside the container, under
`${JIRA_HOME}/logs/`. If you wish to expose this outside the container (e.g. to
be aggregated by logging system) this directory can be a data volume or bind
mount. Additionally, Tomcat-specific logs are written to
`/opt/atlassian/jira/logs/`.

# Upgrades

To upgrade to a more recent version of Jira you can simply stop the `jira` container and start a new one based on a more recent image:

    docker stop jira
    docker rm jira
    docker run ... (See above)

As your data is stored in the data volume directory on the host it will still  be available after the upgrade.

_Note: Please make sure that you **don't** accidentally remove the `jira` container and its volumes using the `-v` option._

# Backup

For evaluations you can use the built-in database that will store its files in the Jira home directory. In that case it is sufficient to create a backup archive of the docker volume.

If you're using an external database, you can configure Jira to make a backup automatically each night. This will back up the current state, including the database to the `jiraVolume` docker volume, which can then be archived. Alternatively you can backup the database separately, and continue to create a backup archive of the docker volume to back up the Jira Home directory.

Read more about data recovery and backups: [https://confluence.atlassian.com/adminjiraserver071/backing-up-data-802592964.html](https://confluence.atlassian.com/adminjiraserver071/backing-up-data-802592964.html)

# Versioning

The `latest` tag matches the most recent release of Atlassian Jira Software, Jira Core or Jira Service Desk. Thus `atlassian/jira-software:latest` will use the newest version of Jira available.

Alternatively you can use a specific major, major.minor, or major.minor.patch version of Jira by using a version number tag:

* `atlassian/jira-software:8`
* `atlassian/jira-software:8.3`
* `atlassian/jira-software:8.3.0`

* `atlassian/jira-servicedesk:4`
* `atlassian/jira-servicedesk:4.3`
* `atlassian/jira-servicedesk:4.3.0`

* `atlassian/jira-core:8`
* `atlassian/jira-core:8.3`
* `atlassian/jira-core:8.3.0`

All versions from 7.13+ are available

# License

Copyright © 2019 Atlassian Corporation Pty Ltd.
Licensed under the Apache License, Version 2.0.

[docker-expose]: https://docs.docker.com/v17.09/engine/userguide/networking/default_network/binding/
