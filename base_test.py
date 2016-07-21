import http.client
from os import path
from time import sleep
import random

from docker import Client as DockerClient
import redis


class BaseTest:
    def __init__(self, redis_testing_data):
        self.docker_cli = DockerClient(base_url='unix://var/run/docker.sock')
        # i wanna run the test more than once at the same time (to avoid to crossing of the services)
        self.port_tail = random.randrange(99)
        self.redis_testing_data = redis_testing_data

    def __enter__(self):
        self._load_redis_instance()
        self._load_webapp_instance()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # kill'em all
        self.docker_cli.remove_container('redis{}'.format(self.port_tail), force=True)
        self.docker_cli.remove_container('subapp{}'.format(self.port_tail), force=True)

    def http_test(self, request: tuple):
        conn = http.client.HTTPConnection("127.0.0.1", port=8000 + self.port_tail)

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

    def _load_redis_instance(self):
        redis_container = self.docker_cli.create_container('redis:latest',
                                                           ports=[6300 + self.port_tail],
                                                           name='redis{}'.format(self.port_tail))
        self.docker_cli.start(redis_container.get('Id'), port_bindings={6379: 6300 + self.port_tail})

        while True:
            # ehm.. we've gotta wait for start of the Redis instance
            try:
                redis_instance = redis.Redis(host='localhost', port=6300 + self.port_tail)
                redis_instance.set('testing_key', self.redis_testing_data)
                break
            except redis.exceptions.ConnectionError:
                sleep(0.1)

    def _load_webapp_instance(self):
        # this 2 lines just build the project subapp - the app will be ready on a local service registry
        app_path = path.join(path.dirname(path.realpath(__file__)), 'subapp')
        self.docker_cli.build(path=app_path, rm=True, tag='heureka/subapp')

        host_config = self.docker_cli.create_host_config(links=[('redis{}'.format(self.port_tail), 'redis')])
        container = self.docker_cli.create_container('heureka/subapp:latest',
                                                     name='subapp{}'.format(self.port_tail),
                                                     ports=[8000],
                                                     host_config=host_config)
        self.docker_cli.start(container.get('Id'), binds={}, port_bindings={8000: 8000 + self.port_tail})


class BaseTest2(BaseTest):
    pass  # todo: do testing docker tree trough two and more webservices (py.test <-> service_1 <-> service_2 <-> redis)




