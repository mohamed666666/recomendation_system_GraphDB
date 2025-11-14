from entities import User, Movie, like, rating, watch, favorite, Actor, movieActors
from schemas import (
    UserCreate, UserRead,
    MovieCreate, MovieRead,
    LikeCreate, LikeRead,
    RatingCreate, RatingRead,
    WatchCreate, WatchRead,
    FavoriteCreate, FavoriteRead,
    ActorCreate, ActorRead,
    MovieActorCreate, MovieActorRead,
)

class UserMapper:

    def to_entity(self, schema: UserCreate) -> User:
        return User(
            name=schema.name,
            email=schema.email,
            password=schema.password
        )
    def to_schema(self, entity: User) -> UserRead:
        return UserRead(
            id=entity.id,
            name=entity.name,
            email=entity.email
        )

class MovieMapper:
    def to_entity(self, schema: MovieCreate) -> Movie:
        return Movie(
            title=schema.title,
            description=schema.description,
            year=schema.year,
            genre=schema.genre
        )
    def to_schema(self, entity: Movie) -> MovieRead:
        return MovieRead(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            year=entity.year,
            genre=entity.genre
        )


class LikeMapper:
    def to_entity(self, schema: LikeCreate) -> like:
        return like(
            user_id=schema.user_id,
            movie_id=schema.movie_id
        )
    def to_schema(self, entity: like) -> LikeRead:
        return LikeRead(
            id=entity.id,
            user_id=entity.user_id,
            movie_id=entity.movie_id
        )


class RatingMapper:
    def to_entity(self, schema: RatingCreate) -> rating:
        return rating(
            user_id=schema.user_id,
            movie_id=schema.movie_id,
            rating=schema.rating
        )
    def to_schema(self, entity: rating) -> RatingRead:
        return RatingRead(
            id=entity.id,
            user_id=entity.user_id,
            movie_id=entity.movie_id,
            rating=entity.rating
        )


class WatchMapper:
    def to_entity(self, schema: WatchCreate) -> watch:
        return watch(
            user_id=schema.user_id,
            movie_id=schema.movie_id
        )
    def to_schema(self, entity: watch) -> WatchRead:
        return WatchRead(
            id=entity.id,
            user_id=entity.user_id,
            movie_id=entity.movie_id
        )


class FavoriteMapper:
    def to_entity(self, schema: FavoriteCreate) -> favorite:
        return favorite(
            user_id=schema.user_id,
            movie_id=schema.movie_id
        )
    def to_schema(self, entity: favorite) -> FavoriteRead:
        return FavoriteRead(
            id=entity.id,
            user_id=entity.user_id,
            movie_id=entity.movie_id
        )


class ActorMapper:
    def to_entity(self, schema: ActorCreate) -> Actor:
        return Actor(
            name=schema.name,
            bio=schema.bio
        )
    def to_schema(self, entity: Actor) -> ActorRead:
        return ActorRead(
            id=entity.id,
            name=entity.name,
            bio=entity.bio
        )


class MovieActorMapper:
    def to_entity(self, schema: MovieActorCreate) -> movieActors:
        return movieActors(
            movie_id=schema.movie_id,
            actor_id=schema.actor_id
        )
    def to_schema(self, entity: movieActors) -> MovieActorRead:
        return MovieActorRead(
            id=entity.id,
            movie_id=entity.movie_id,
            actor_id=entity.actor_id
        )
