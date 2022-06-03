import datetime
import math

import requests
from google.cloud import ndb

from backend import error


class NotFound(error.Error):
    pass


class Movie(ndb.Model):
    created = ndb.DateTimeProperty(indexed=False)
    title = ndb.StringProperty(required=True, indexed=True)
    year = ndb.StringProperty(indexed=True)
    imdbID = ndb.StringProperty(indexed=True)
    poster = ndb.StringProperty()
    normalized_title = ndb.ComputedProperty(
        lambda self: self.title and self.title.lower(), indexed=True
    )

    @classmethod
    def _query(cls, *filters, **kwargs):
        count = super()._query().count()
        if abs(count - 100) > 10:
            for page in range(1, math.ceil((100 - count) / 10) + 1):
                search_word = "holiday"
                movies = requests.get(
                    f"{cls._api_host}?s={search_word}&type=movie"
                    f"&apikey={cls._apikey}&page={page}"
                ).json()
                for item in movies.get("Search", []):
                    cls.create(
                        title=item.get("Title"),
                        year=item.get("Year"),
                        imdbID=item.get("imdbID"),
                        poster=item.get("Poster"),
                    )
                    count += 1
                    if count >= 100:
                        break
            # count = super()._query().count()
            # print(f"{count} movies in database")
        return super()._query(*filters, **kwargs)

    _apikey = "3a396d25"
    _api_host = "https://www.omdbapi.com/"
    query = _query

    @classmethod
    def get_by_title(cls, title):
        entities = cls.query(cls.title == title).fetch(1)
        return entities[0] if entities else None

    @classmethod
    def list(cls, offset=0, limit=10):
        return cls.query().order(Movie.title).fetch(offset=offset, limit=limit)

    @classmethod
    def create(cls, title: str, year=None, imdbID=None, poster=None):
        entity = cls(
            created=datetime.datetime.now(),
            title=title,
            year=year,
            imdbID=imdbID,
            poster=poster,
        )

        if all(x is None for x in (year, imdbID, poster)):
            resp = requests.get(
                f"{cls._api_host}?t={title}&apikey={cls._apikey}"
            ).json()
            entity.year = resp.get("Year")
            entity.imdbID = resp.get("imdbID")
            entity.poster = resp.get("Poster")

        entity.put()
        return entity

    @classmethod
    def delete(cls, imdbID):
        entities = cls.query(cls.imdbID == imdbID).fetch(1)
        if entities:
            entities[0].key.delete()
            return True
        return False

    @property
    def id(self):
        return self.key.urlsafe().decode("utf-8")

    def __hash__(self):
        return hash((self.__class__.__name__, self.id))
