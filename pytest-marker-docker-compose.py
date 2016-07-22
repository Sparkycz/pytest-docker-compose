import pytest
import time
import subprocess
import compose.cli.command
import pdb

class DockerGroup(object):

    def __init__(self, name, dir):
        self.project = compose.cli.command.get_project(project_dir=dir, project_name=name)
        self.containers = []

    def get_container(self, name):
        container = [container for container in self.containers if container.service == name][0]
        container.inspect()
        return DockerContainer(container)

    def __enter__(self):
        #subprocess.call(['docker-compose -f {file} -p {name} up -d web'.format(file=self.file, name=self.name)], shell=True)
        self.containers = self.project.up()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        #subprocess.call("docker-compose -f {file} -p {name} down -f".format(file=self.file, name=self.name), shell=True)

class DockerContainer(object):

    def __init__(self, container):
        self.container = container

    def exposed_port(self, internal_port):
        host = self.container.get_local_port(8000)
        port = host.split(":")[1]
        return int(port)

    @property
    def id(self):
        return self.container.id

    @property
    def ip(self):
        return list(self.container.dictionary['NetworkSettings']['Networks'].values())[0]['IPAddress']

@pytest.yield_fixture(scope="module")
def docker_group(request):
    file = request.param
    name = str(time.time())
    with DockerGroup(name, file) as docker_group:
        yield docker_group


@pytest.mark.parametrize('docker_group', ['./subapp'], indirect=True)
def test(docker_group):
    docker_group.get_container('web').exposed_port(8000)
    assert (docker_group.get_container('redis').ip == 'whatever')
