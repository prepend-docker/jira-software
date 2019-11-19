import pytest

import docker
import requests


MAC_PRODUCT_KEY = 'jira-software'
DOCKER_VERSION_ARG = 'JIRA_VERSION'
DOCKERFILES = ['Dockerfile']
IMAGE_NAME = 'jira-software:dev'

# This fixture cleans up running containers whose base image matches IMAGE_NAME after each test
@pytest.fixture
def docker_cli():
    docker_cli = docker.from_env()
    yield docker_cli
    for container in docker_cli.containers.list():
        if IMAGE_NAME in container.image.tags:
            container.remove(force=True)
    


@pytest.fixture(scope='module', params=DOCKERFILES)
def image(request):
    r = requests.get(f'https://marketplace.atlassian.com/rest/2/products/key/{MAC_PRODUCT_KEY}/versions/latest')
    version = r.json().get('name')
    buildargs = {DOCKER_VERSION_ARG: version}
    docker_cli = docker.from_env()
    image = docker_cli.images.build(path='.',
                                    tag=IMAGE_NAME,
                                    buildargs=buildargs,
                                    dockerfile=request.param,
                                    rm=True)[0]
    return image