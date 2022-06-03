from backend import test, movie


class TestMovie(test.TestCase):
    def test_create(self):
        obj = movie.Movie.create(title="Titanic")
        self.assertEqual(obj, movie.Movie.get_by_title(obj.title))
        self.assertTrue(obj.year == "1997")
        self.assertTrue(obj.imdbID == "tt0120338")

    def test_get_by_title(self):
        obj = movie.Movie.get_by_title(title="Shrek")
        self.assertEqual(obj, None)
        obj = movie.Movie.create(title="Shrek")
        self.assertEqual(obj.title, "Shrek")
        self.assertEqual(obj.year, "2001")
        self.assertEqual(obj.imdbID, "tt0126029")

    def test_list(self):
        movies = movie.Movie.list()
        self.assertEqual(len(movies), 10)
        titles = [x.title for x in movies]
        self.assertEqual(titles, sorted(titles))

    def test_delete(self):
        obj = movie.Movie.create(title="Titanic")
        resp = movie.Movie.delete(obj.imdbID)
        self.assertTrue(resp)
        obj = movie.Movie.get_by_title(title="Titanic")
        self.assertIsNone(obj)


class TestMovieApi(test.TestCase):
    def test_list(self):
        resp = self.api_client.post("movie.list")
        self.assertEqual(len(resp["movies"]), 10)

    def test_list_with_limit(self):
        first20 = self.api_client.post("movie.list", dict(offset=0, limit=20))
        from10to25 = self.api_client.post("movie.list", dict(offset=10, limit=15))

        self.assertEqual(len(first20["movies"]), 20)
        self.assertEqual(len(from10to25["movies"]), 15)
        # compare equality
        self.assertEqual(from10to25["movies"][:10], first20["movies"][10:])

    def test_get(self):
        single = self.api_client.post("movie.get", dict(title="Holiday"))
        single.pop("poster")
        self.assertEqual(
            single, {"title": "Holiday", "year": "1938", "imdbID": "tt0030241"}
        )

    def test_post(self):
        obj = self.api_client.post("movie.create", dict(title="Shrek"))
        obj.pop("poster")
        self.assertEqual(
            obj,
            {
                "title": "Shrek",
                "year": "2001",
                "imdbID": "tt0126029",
            },
        )

    def test_delete(self):
        self.api_client.post("movie.create", dict(title="Titanic"))
        titanic = self.api_client.post("movie.get", dict(title="Titanic"))
        titanic.pop("poster")
        self.assertEqual(
            titanic,
            {
                "title": "Titanic",
                "year": "1997",
                "imdbID": "tt0120338",
            },
        )
        # delete a movie without auth
        delete_result = self.api_client.post(
            "movie.delete", dict(imdbID=titanic["imdbID"])
        )
        self.assertEqual(
            delete_result,
            {
                "error": {
                    "code": "400 Bad Request",
                    "error_name": "Unauthorized",
                    "message": "Invalid or expired access token",
                }
            },
        )

        # auth test user
        resp = self.api_client.post(
            "user.create", dict(email="test@gmail.com", password="test")
        )
        access_token = resp.get("access_token")
        self.assertEqual(resp.get("error"), None)

        # delete a movie with auth
        delete_result = self.api_client.post(
            "movie.delete",
            dict(imdbID=titanic["imdbID"]),
            headers=dict(authorization=access_token),
        )
        self.assertEqual(delete_result, {"success": True})

        resp = self.api_client.post("movie.get", dict(title="Titanic"))
        self.assertEqual(
            resp.get("error"),
            {
                "code": "400 Bad Request",
                "error_name": "NotFound",
                "message": 'No movie found with title: "Titanic"',
            },
        )
