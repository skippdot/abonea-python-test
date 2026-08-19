from google.cloud import logging
from google.cloud.logging import Logger


class Client:
    def __init__(self, project=None, namespace=None, credentials=None):
        self.project = project or "stub"
        self.namespace = namespace
        self.credentials = credentials

    def logger(self, name, *, labels=None, resource=None):
        return Logger(name, client=self, labels=labels, resource=resource)


logging.Client = Client
