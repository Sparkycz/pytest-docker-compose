import pytest
import os

from pytest_docker_compose.fixture import docker_group


docker_compose_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'subapp')


@pytest.mark.usefixtures('docker_group')
@pytest.mark.parametrize('docker_group', [docker_compose_path], indirect=True)
def test(docker_group):
    docker_group.get_container('web').exposed_port(8080)
    print(docker_group.get_container('redis').ip)
