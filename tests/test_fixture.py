import os
import http.client
from time import sleep

import redis
import pytest

from pytest_docker_compose.fixture import docker_group


docker_compose_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'examples', 'subapp')


@pytest.mark.usefixtures('docker_group')
@pytest.fixture
def testing_instances(docker_group):
    redis_port = docker_group.get_container('redis').exposed_port(6379)
    while True:
        # ehm.. we've gotta wait for start of the Redis instance
        try:
            redis_instance = redis.Redis(port=redis_port)
            break
        except redis.exceptions.ConnectionError:
            sleep(0.1)

    web_port = docker_group.get_container('web').exposed_port(8000)
    http_connection = http.client.HTTPConnection("127.0.0.1", port=web_port)

    while True:
        # ehm.. we've gotta wait for start of the Flask instance
        try:
            http_connection.request("GET", "/ping")  # every service in Heureka must have `/ping` for service-control as well
            http_connection.getresponse()
            break
        except http.client.RemoteDisconnected:
            sleep(0.1)

    return redis_instance, http_connection


@pytest.mark.parametrize('docker_group', [docker_compose_path], indirect=True)
def test_integration(testing_instances):
    redis_instance, http_connection = testing_instances
    testing_data = b'whatever'

    redis_instance.set('testing_key', testing_data)

    http_connection.request("GET", "/get-hello")
    actual = http_connection.getresponse().read()

    assert testing_data == actual
