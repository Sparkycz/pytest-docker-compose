import http.client
from time import sleep
import random
import subprocess
import redis

class DockerGroup(object):

    def __init__(self, name, file="docker-compose.yml"):
        self.name = name
        self.file = file

    def get_container(self, name):
        return DockerContainer(self)

    def run(self):
        subprocess.call(['docker-compose -f {file} -p {name} up -d web'.format(file=self.file, name=self.name)], shell=True)

    def kill(self):
        subprocess.call("docker-compose -f {file} -p {name} kill".format(file=self.file, name=self.name), shell=True)

class DockerContainer(object):

    def __init__(self, docker_group):
        self.docker_group = docker_group

    def exposed_port(self, internal_port):
        file = self.docker_group.file
        name = self.docker_group.name
        web_host = subprocess.check_output('docker-compose -f {file} -p {name} port web {port}'.format(file=file, name=name, port=internal_port), shell=True).decode('ascii').strip()
        return web_host.split(":")[1]

    @property
    def id(self):
        file = self.docker_group.file
        name = self.docker_group.name
        return subprocess.check_output(['docker-compose -f {file} -p {name} ps -q redis'.format(file=file, name=name)], shell=True).decode('ascii').strip()

    @property
    def ip(self):
        return subprocess.check_output(["docker inspect {cid} | grep IPAddress | cut -d '\"' -f 4 | grep . ".format(cid=self.id)], shell=True)


class BaseTest:
    def __init__(self, redis_testing_data):
        self.redis_testing_data = redis_testing_data
        id = random.randint(1,100)
        self.docker_group = DockerGroup(id, './subapp/docker-compose.yml')

    def __enter__(self):
        self.docker_group.run()
        self._set_redis_instance()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.docker_group.kill()

    def http_test(self, request: tuple):
        web_container = self.docker_group.get_container('web')
        conn = http.client.HTTPConnection("127.0.0.1", port=web_container.exposed_port(8000))

        while True:
            # ehm.. we've gotta wait for start of the Flask instance
            try:
                conn.request("GET", "/ping")  # every service in Heureka must have `/ping` for service-control as well
                conn.getresponse()
                break
            except http.client.RemoteDisconnected:
                sleep(0.1)

        conn.request(*request)
        return conn.getresponse().read()

    def _set_redis_instance(self):
        while True:
            # ehm.. we've gotta wait for start of the Redis instance
            try:
                redis_container = self.docker_group.get_container('redis')
                redis_instance = redis.Redis(host=redis_container.ip, port=6379)
                redis_instance.set('testing_key', self.redis_testing_data)
                break
            except redis.exceptions.ConnectionError:
                sleep(0.1)


class BaseTest2(BaseTest):
    pass  # todo: do testing docker tree trough two and more webservices (py.test <-> service_1 <-> service_2 <-> redis)




