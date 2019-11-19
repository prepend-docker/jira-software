import pytest

import io
import logging
import tarfile
import time
import xml.etree.ElementTree as etree

import requests


# Helper function to get a file-like object from an image
def get_fileobj_from_container(container, filepath):
    time.sleep(0.5) # Give container a moment if just started
    stream, stat = container.get_archive(filepath)
    f = io.BytesIO()
    for chunk in stream:
        f.write(chunk)
    f.seek(0)
    with tarfile.open(fileobj=f, mode='r') as tar:
        filename = tar.getmembers()[0].name
        file = tar.extractfile(filename)
    return file



def test_server_xml_defaults(docker_cli, image):
    container = docker_cli.containers.run(image, detach=True)
    server_xml = get_fileobj_from_container(container, '/opt/atlassian/jira/conf/server.xml')
    xml = etree.parse(server_xml)
    connector = xml.find('.//Connector')
    context = xml.find('.//Context')

    assert connector.get('port') == '8080'
    assert connector.get('maxThreads') == '100'
    assert connector.get('minSpareThreads') == '10'
    assert connector.get('connectionTimeout') == '20000'
    assert connector.get('enableLookups') == 'false'
    assert connector.get('protocol') == 'HTTP/1.1'
    assert connector.get('acceptCount') == '10'
    assert connector.get('secure') == 'false'
    assert connector.get('scheme') == 'http'
    assert connector.get('proxyName') == ''
    assert connector.get('proxyPort') == ''


def test_server_xml_params(docker_cli, image):
    environment = {
        'ATL_TOMCAT_MGMT_PORT': '8006',
        'ATL_TOMCAT_PORT': '9090',
        'ATL_TOMCAT_MAXTHREADS': '201',
        'ATL_TOMCAT_MINSPARETHREADS': '11',
        'ATL_TOMCAT_CONNECTIONTIMEOUT': '20001',
        'ATL_TOMCAT_ENABLELOOKUPS': 'true',
        'ATL_TOMCAT_PROTOCOL': 'HTTP/2',
        'ATL_TOMCAT_ACCEPTCOUNT': '11',
        'ATL_TOMCAT_SECURE': 'true',
        'ATL_TOMCAT_SCHEME': 'https',
        'ATL_PROXY_NAME': 'jira.atlassian.com',
        'ATL_PROXY_PORT': '443',
        'ATL_TOMCAT_CONTEXTPATH': '/myjira',
    }
    container = docker_cli.containers.run(image, environment=environment, detach=True)
    server_xml = get_fileobj_from_container(container, '/opt/atlassian/jira/conf/server.xml')
    xml = etree.parse(server_xml)
    server = xml.getroot()
    connector = xml.find('.//Connector')
    context = xml.find('.//Context')

    assert server.get('port') == environment.get('ATL_TOMCAT_MGMT_PORT')

    assert connector.get('port') == environment.get('ATL_TOMCAT_PORT')
    assert connector.get('maxThreads') == environment.get('ATL_TOMCAT_MAXTHREADS')
    assert connector.get('minSpareThreads') == environment.get('ATL_TOMCAT_MINSPARETHREADS')
    assert connector.get('connectionTimeout') == environment.get('ATL_TOMCAT_CONNECTIONTIMEOUT')
    assert connector.get('enableLookups') == environment.get('ATL_TOMCAT_ENABLELOOKUPS')
    assert connector.get('protocol') == environment.get('ATL_TOMCAT_PROTOCOL')
    assert connector.get('acceptCount') == environment.get('ATL_TOMCAT_ACCEPTCOUNT')
    assert connector.get('secure') == environment.get('ATL_TOMCAT_SECURE')
    assert connector.get('scheme') == environment.get('ATL_TOMCAT_SCHEME')
    assert connector.get('proxyName') == environment.get('ATL_PROXY_NAME')
    assert connector.get('proxyPort') == environment.get('ATL_PROXY_PORT')

    assert context.get('path') == environment.get('ATL_TOMCAT_CONTEXTPATH')


def test_dbconfig_xml_defaults(docker_cli, image):
    environment = {
        'ATL_DB_TYPE': 'postgres72',
        'ATL_DB_DRIVER': 'org.postgresql.Driver',
        'ATL_JDBC_URL': 'jdbc:postgresql://mypostgres.mycompany.org:5432/jiradb',
        'ATL_JDBC_USER': 'jiradbuser',
        'ATL_JDBC_PASSWORD': 'jiradbpassword',
    }
    container = docker_cli.containers.run(image, environment=environment, detach=True)
    dbconfig_xml = get_fileobj_from_container(container, '/var/atlassian/application-data/jira/dbconfig.xml')
    xml = etree.parse(dbconfig_xml)

    assert xml.findtext('.//pool-min-size') == '20'
    assert xml.findtext('.//pool-max-size') == '100'
    assert xml.findtext('.//pool-min-idle') == '10'
    assert xml.findtext('.//pool-max-idle') == '20'

    assert xml.findtext('.//pool-max-wait') == '30000'
    assert xml.findtext('.//validation-query') == 'select 1'
    assert xml.findtext('.//time-between-eviction-runs-millis') == '30000'
    assert xml.findtext('.//min-evictable-idle-time-millis') == '5000'

    assert xml.findtext('.//pool-remove-abandoned') == 'true'
    assert xml.findtext('.//pool-remove-abandoned-timeout') == '300'
    assert xml.findtext('.//pool-test-while-idle') == 'true'
    assert xml.findtext('.//pool-test-on-borrow') == 'false'


def test_dbconfig_xml_params(docker_cli, image):
    environment = {
        'ATL_DB_TYPE': 'postgres72',
        'ATL_DB_DRIVER': 'org.postgresql.Driver',
        'ATL_JDBC_URL': 'jdbc:postgresql://mypostgres.mycompany.org:5432/jiradb',
        'ATL_JDBC_USER': 'jiradbuser',
        'ATL_JDBC_PASSWORD': 'jiradbpassword',
        'ATL_DB_MAXIDLE': '21',
        'ATL_DB_MAXWAITMILLIS': '30001',
        'ATL_DB_MINEVICTABLEIDLETIMEMILLIS': '5001',
        'ATL_DB_MINIDLE': '11',
        'ATL_DB_POOLMAXSIZE': '101',
        'ATL_DB_POOLMINSIZE': '21',
        'ATL_DB_REMOVEABANDONED': 'false',
        'ATL_DB_REMOVEABANDONEDTIMEOUT': '301',
        'ATL_DB_TESTONBORROW': 'true',
        'ATL_DB_TESTWHILEIDLE': 'false',
        'ATL_DB_TIMEBETWEENEVICTIONRUNSMILLIS': '30001',
        'ATL_DB_VALIDATIONQUERY': 'select 2',
    }
    container = docker_cli.containers.run(image, environment=environment, detach=True)
    dbconfig_xml = get_fileobj_from_container(container, '/var/atlassian/application-data/jira/dbconfig.xml')
    xml = etree.parse(dbconfig_xml)

    assert xml.findtext('.//database-type') == environment.get('ATL_DB_TYPE')
    assert xml.findtext('.//driver-class') == environment.get('ATL_DB_DRIVER')
    assert xml.findtext('.//url') == environment.get('ATL_JDBC_URL')
    assert xml.findtext('.//username') == environment.get('ATL_JDBC_USER')
    assert xml.findtext('.//password') == environment.get('ATL_JDBC_PASSWORD')

    assert xml.findtext('.//pool-min-size') == environment.get('ATL_DB_POOLMINSIZE')
    assert xml.findtext('.//pool-max-size') == environment.get('ATL_DB_POOLMAXSIZE')
    assert xml.findtext('.//pool-min-idle') == environment.get('ATL_DB_MINIDLE')
    assert xml.findtext('.//pool-max-idle') == environment.get('ATL_DB_MAXIDLE')
    assert xml.findtext('.//pool-max-wait') == environment.get('ATL_DB_MAXWAITMILLIS')
    assert xml.findtext('.//validation-query') == environment.get('ATL_DB_VALIDATIONQUERY')
    assert xml.findtext('.//time-between-eviction-runs-millis') == environment.get('ATL_DB_TIMEBETWEENEVICTIONRUNSMILLIS')
    assert xml.findtext('.//min-evictable-idle-time-millis') == environment.get('ATL_DB_MINEVICTABLEIDLETIMEMILLIS')
    assert xml.findtext('.//pool-remove-abandoned') == environment.get('ATL_DB_REMOVEABANDONED')
    assert xml.findtext('.//pool-remove-abandoned-timeout') == environment.get('ATL_DB_REMOVEABANDONEDTIMEOUT')
    assert xml.findtext('.//pool-test-while-idle') == environment.get('ATL_DB_TESTWHILEIDLE')
    assert xml.findtext('.//pool-test-on-borrow') == environment.get('ATL_DB_TESTONBORROW')


def test_cluster_properties_defaults(docker_cli, image):
    environment = {
        'CLUSTERED': 'true',
    }
    container = docker_cli.containers.run(image, environment=environment, detach=True)
    cluster_properties = get_fileobj_from_container(container, '/var/atlassian/application-data/jira/cluster.properties')
    properties_str = cluster_properties.read().decode().strip().split('\n')
    properties = dict(item.split("=") for item in properties_str)
    container_id = get_fileobj_from_container(container, '/etc/container_id').read().decode().strip()

    assert properties.get('jira.node.id') == container_id
    assert properties.get('jira.shared.home') == '/var/atlassian/application-data/jira/shared'
    assert properties.get('ehcache.peer.discovery') is None
    assert properties.get('ehcache.listener.hostName') is None
    assert properties.get('ehcache.listener.port') is None
    assert properties.get('ehcache.object.port') is None
    assert properties.get('ehcache.listener.socketTimeoutMillis') is None
    assert properties.get('ehcache.multicast.address') is None
    assert properties.get('ehcache.multicast.port') is None
    assert properties.get('ehcache.multicast.timeToLive') is None
    assert properties.get('ehcache.multicast.hostName') is None


def test_cluster_properties_params(docker_cli, image):
    environment = {
        'CLUSTERED': 'true',
        'JIRA_NODE_ID': 'jiradc1',
        'JIRA_SHARED_HOME': '/data/shared',
        'EHCACHE_PEER_DISCOVERY': 'default',
        'EHCACHE_LISTENER_HOSTNAME': 'jiradc1.local',
        'EHCACHE_LISTENER_PORT': '40002',
        'EHCACHE_OBJECT_PORT': '40003',
        'EHCACHE_LISTENER_SOCKETTIMEOUTMILLIS': '2001',
        'EHCACHE_MULTICAST_ADDRESS': '1.2.3.4',
        'EHCACHE_MULTICAST_PORT': '40004',
        'EHCACHE_MULTICAST_TIMETOLIVE': '1000',
        'EHCACHE_MULTICAST_HOSTNAME': 'jiradc1.local',
    }
    container = docker_cli.containers.run(image, environment=environment, detach=True)
    cluster_properties = get_fileobj_from_container(container, '/var/atlassian/application-data/jira/cluster.properties')
    properties_str = cluster_properties.read().decode().strip().split('\n')
    properties = dict(item.split("=") for item in properties_str)

    assert properties.get('jira.node.id') == environment.get('JIRA_NODE_ID')
    assert properties.get('jira.shared.home') == environment.get('JIRA_SHARED_HOME')
    assert properties.get('ehcache.peer.discovery') == environment.get('EHCACHE_PEER_DISCOVERY')
    assert properties.get('ehcache.listener.hostName') == environment.get('EHCACHE_LISTENER_HOSTNAME')
    assert properties.get('ehcache.listener.port') == environment.get('EHCACHE_LISTENER_PORT')
    assert properties.get('ehcache.object.port') == environment.get('EHCACHE_OBJECT_PORT')
    assert properties.get('ehcache.listener.socketTimeoutMillis') == environment.get('EHCACHE_LISTENER_SOCKETTIMEOUTMILLIS')
    assert properties.get('ehcache.multicast.address') == environment.get('EHCACHE_MULTICAST_ADDRESS')
    assert properties.get('ehcache.multicast.port') == environment.get('EHCACHE_MULTICAST_PORT')
    assert properties.get('ehcache.multicast.timeToLive') == environment.get('EHCACHE_MULTICAST_TIMETOLIVE')
    assert properties.get('ehcache.multicast.hostName') == environment.get('EHCACHE_MULTICAST_HOSTNAME')


def test_jvm_args(docker_cli, image):
    environment = {
        'JVM_MINIMUM_MEMORY': '383m',
        'JVM_MAXIMUM_MEMORY': '2047m',
        'JVM_SUPPORT_RECOMMENDED_ARGS': '-verbose:gc',
    }
    container = docker_cli.containers.run(image, environment=environment, detach=True)
    time.sleep(0.5) # JVM doesn't start immediately when container runs
    procs = container.exec_run('ps aux')
    procs_list = procs.output.decode().split('\n')
    jvm = [proc for proc in procs_list if '-Datlassian.standalone=JIRA' in proc][0]
    assert f'-Xms{environment.get("JVM_MINIMUM_MEMORY")}' in jvm
    assert f'-Xmx{environment.get("JVM_MAXIMUM_MEMORY")}' in jvm
    assert environment.get('JVM_SUPPORT_RECOMMENDED_ARGS') in jvm


def test_first_run_state(docker_cli, image):
    container = docker_cli.containers.run(image, ports={8080: 8080}, detach=True)
    for i in range(20):
        try:
            r = requests.get('http://localhost:8080/status')
        except requests.exceptions.ConnectionError:
            pass
        else:
            if r.status_code == 200:
                state = r.json().get('state')
                assert state in ('STARTING', 'FIRST_RUN')
                return
        time.sleep(1)
    raise TimeoutError


def test_java_in_jira_user_path(docker_cli, image):
    container = docker_cli.containers.run(image, detach=True)
    proc = container.exec_run('su -c "which java" jira')
    assert len(proc.output) > 0


def test_non_root_user(docker_cli, image):
    RUN_UID = 2001
    RUN_GID = 2001
    container = docker_cli.containers.run(image, user=f'{RUN_UID}:{RUN_GID}', detach=True)
    time.sleep(0.5) # JVM doesn't start immediately when container runs
    procs = container.exec_run('ps aux')
    procs_list = procs.output.decode().split('\n')
    jvm = [proc for proc in procs_list if '-Datlassian.standalone=JIRA' in proc][0]
    assert b'WARNING' in container.logs()