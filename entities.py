

class User:
    def __init__(self, id: int | None = None, name: str = "", email: str = "", password: str = ""):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password": self.password
        }

    @staticmethod
    def from_dict(data: dict):
        return User(data["id"], data["name"], data["email"], data["password"])



class Movie:
    def __init__(self, id: int | None = None, title: str = "", description: str = "", year: int = 0, genre: str = ""):
        self.id = id
        self.title = title
        self.description = description
        self.year = year
        self.genre = genre

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "year": self.year,
            "genre": self.genre
        }

    @staticmethod
    def from_dict(data: dict):
        return Movie(data["id"], data["title"], data["description"], data["year"], data["genre"])



class movieActors:
    def __init__(self, id: int | None = None, movie_id: int = 0, actor_id: int = 0):
        self.id = id
        self.movie_id = movie_id
        self.actor_id = actor_id

    def to_dict(self):
        return {
            "id": self.id,
            "movie_id": self.movie_id,
            "actor_id": self.actor_id
        }

    @staticmethod
    def from_dict(data: dict):
        return movieActors(data["id"], data["movie_id"], data["actor_id"])

class like:
    def __init__(self, id: int | None = None, user_id: int = 0, movie_id: int = 0):
        self.id = id
        self.user_id = user_id
        self.movie_id = movie_id

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "movie_id": self.movie_id
        }

    @staticmethod
    def from_dict(data: dict):
        return like(data["id"], data["user_id"], data["movie_id"])

class rating:
    def __init__(self, id: int | None = None, user_id: int = 0, movie_id: int = 0, rating: int = 0):
        self.id = id
        self.user_id = user_id
        self.movie_id = movie_id
        self.rating = rating

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "movie_id": self.movie_id,
            "rating": self.rating
        }
    @staticmethod
    def from_dict(data: dict):
        return rating(data["id"], data["user_id"], data["movie_id"], data["rating"])

class watch:
    def __init__(self, id: int | None = None, user_id: int = 0, movie_id: int = 0):
        self.id = id
        self.user_id = user_id
        self.movie_id = movie_id

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "movie_id": self.movie_id
        }
    @staticmethod
    def from_dict(data: dict):
        return watch(data["id"], data["user_id"], data["movie_id"])

class favorite:
    def __init__(self, id: int | None = None, user_id: int = 0, movie_id: int = 0):
        self.id = id
        self.user_id = user_id
        self.movie_id = movie_id
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "movie_id": self.movie_id
        }
    @staticmethod
    def from_dict(data: dict):
        return favorite(data["id"], data["user_id"], data["movie_id"])



class Actor:
    def __init__(self, id: int | None = None, name: str = "", bio: str = ""):
        self.id = id
        self.name = name
        self.bio = bio
      
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "bio": self.bio,
          
        }
    @staticmethod
    def from_dict(data: dict):
        return Actor(data["id"], data["name"], data["bio"])



