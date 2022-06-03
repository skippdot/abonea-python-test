from backend import api, movie
from backend.movie import NotFound
from backend.oauth2 import oauth2
from backend.swagger import swagger
from backend.wsgi import remote, messages


class MovieRequest(messages.Message):
    offset = messages.IntegerField(1, default=0)
    limit = messages.IntegerField(2, default=10)


class TitleRequest(messages.Message):
    title = messages.StringField(1, required=True)


class DeleteRequest(messages.Message):
    imdbID = messages.StringField(1, required=True)


class DeleteResponse(messages.Message):
    success = messages.BooleanField(1)


class MovieResult(messages.Message):
    title = messages.StringField(1)
    year = messages.StringField(2)
    imdbID = messages.StringField(3)
    poster = messages.StringField(4)


class MoviesResponse(messages.Message):
    movies = messages.MessageField(MovieResult, 1, repeated=True)
    # totalResults = messages.IntegerField(2)


class CreateRequest(messages.Message):
    title = messages.StringField(1, required=True)
    year = messages.StringField(2)
    imdbID = messages.StringField(3)
    poster = messages.StringField(4)


@api.endpoint(path="movie", title="OMDB API")
class Movie(remote.Service):
    @swagger("Get 10 movies")
    @remote.method(MovieRequest, MoviesResponse)
    def list(self, request):
        movies = movie.Movie.list(offset=request.offset, limit=request.limit)

        return MoviesResponse(
            movies=[
                MovieResult(
                    title=mov.title,
                    year=mov.year,
                    imdbID=mov.imdbID,
                    poster=mov.poster,
                )
                for mov in movies
            ]
        )

    @swagger("Create a movie")
    @remote.method(CreateRequest, MovieResult)
    def create(self, request):
        item = movie.Movie.create(
            title=request.title,
            year=request.year,
            imdbID=request.imdbID,
            poster=request.poster,
        )
        return MovieResult(
            title=item.title,
            year=item.year,
            imdbID=item.imdbID,
            poster=item.poster,
        )

    @swagger("Get a movie by title")
    @remote.method(TitleRequest, MovieResult)
    def get(self, request):
        item = movie.Movie.get_by_title(request.title)
        if not item:
            raise NotFound('No movie found with title: "%s"' % request.title)
        return MovieResult(
            title=item.title,
            year=item.year,
            imdbID=item.imdbID,
            poster=item.poster,
        )

    @swagger("Delete a movie")
    @oauth2.required()
    @remote.method(DeleteRequest, DeleteResponse)
    def delete(self, request):
        return DeleteResponse(success=movie.Movie.delete(imdbID=request.imdbID))
