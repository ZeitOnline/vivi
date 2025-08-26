import contextlib
import socket

import docker
import requests.exceptions

from .layer import Layer


class DockerLayer(Layer):
    def setUp(self):
        self['docker'] = docker.from_env()

    def tearDown(self):
        self['docker'].close()
        del self['docker']

    def run_container(self, *args, **kw):
        try:
            return self['docker'].containers.run(*args, **kw)
        except requests.exceptions.ConnectionError:
            raise DockerSetupError("Couldn't start docker container, is docker running?")


LAYER = DockerLayer()


class DockerSetupError(requests.exceptions.ConnectionError):
    pass


# Taken from pytest-nginx
def get_random_port():
    s = socket.socket()
    with contextlib.closing(s):
        s.bind(('localhost', 0))
        return s.getsockname()[1]
