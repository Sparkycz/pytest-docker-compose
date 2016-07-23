import pytest
import time

from compose.cli import command


class DockerGroup:
    def __init__(self, name, dir):
        self.project = command.get_project(project_dir=dir, project_name=name)
        self.containers = []

    def get_container(self, name):
        container = [container for container in self.containers if container.service == name][0]
        container.inspect()
        return DockerContainer(container)

    def __enter__(self):
        self.containers = self.project.up()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.project.down(False, False)


class DockerContainer:
    def __init__(self, container):
        self.container = container

    def exposed_port(self, internal_port):
        host = self.container.get_local_port(internal_port)
        port = host.split(":")[1]
        return int(port)

    @property
    def id(self):
        return self.container.id

    @property
    def ip(self):
        networks = self.container.dictionary['NetworkSettings']['Networks']
        first_network = list(networks.values())[0]
        return first_network['IPAddress']


@pytest.yield_fixture(scope="module")
def docker_group(request):
    file = request.param
    name = str(time.time())
    with DockerGroup(name, file) as _docker_group:
        yield _docker_group

