from google.cloud import ndb

from inmemory_datastore_stub import Client

ndb.Client = Client
