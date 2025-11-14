from typing import Optional

from sqlmodel import SQLModel, Field

from entities import User as UserEntity, Movie as MovieEntity, like as LikeEntity, rating as RatingEntity, watch as WatchEntity, favorite as FavoriteEntity, Actor as ActorEntity, movieActors as MovieActorEntity


class User(SQLModel, table=True):
    """SQLModel table for users.

    Attributes:
        id: Primary key.
        name: User display name.
        email: User email address.
        password: Hashed password string.
    """

    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    name: str
    email: str = Field(index=True)
    password: str

    def to_entity(self) -> UserEntity:
        """Convert SQLModel instance to domain entity."""
        return UserEntity(
            id=self.id,
            name=self.name,
            email=self.email,
            password=self.password
        )


class Movie(SQLModel, table=True):
    """SQLModel table for movies."""

    __tablename__ = "movies"

    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    title: str
    description: str
    year: int
    genre: str

    def to_entity(self) -> MovieEntity:
        """Convert SQLModel instance to domain entity."""
        return MovieEntity(
            id=self.id,
            title=self.title,
            description=self.description,
            year=self.year,
            genre=self.genre
        )


class Like(SQLModel, table=True):
    """SQLModel table for user likes on movies."""

    __tablename__ = "likes"

    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    user_id: int = Field(foreign_key="users.id", index=True)
    movie_id: int = Field(foreign_key="movies.id", index=True)

    def to_entity(self) -> LikeEntity:
        """Convert SQLModel instance to domain entity."""
        return LikeEntity(
            id=self.id,
            user_id=self.user_id,
            movie_id=self.movie_id
        )


class Rating(SQLModel, table=True):
    """SQLModel table for movie ratings by users."""

    __tablename__ = "ratings"

    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    user_id: int = Field(foreign_key="users.id", index=True)
    movie_id: int = Field(foreign_key="movies.id", index=True)
    rating: int

    def to_entity(self) -> RatingEntity:
        """Convert SQLModel instance to domain entity."""
        return RatingEntity(
            id=self.id,
            user_id=self.user_id,
            movie_id=self.movie_id,
            rating=self.rating
        )


class Watch(SQLModel, table=True):
    """SQLModel table for user watch events."""

    __tablename__ = "watches"

    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    user_id: int = Field(foreign_key="users.id", index=True)
    movie_id: int = Field(foreign_key="movies.id", index=True)

    def to_entity(self) -> WatchEntity:
        """Convert SQLModel instance to domain entity."""
        return WatchEntity(
            id=self.id,
            user_id=self.user_id,
            movie_id=self.movie_id
        )


class Favorite(SQLModel, table=True):
    """SQLModel table for user favorite movies."""

    __tablename__ = "favorites"

    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    user_id: int = Field(foreign_key="users.id", index=True)
    movie_id: int = Field(foreign_key="movies.id", index=True)

    def to_entity(self) -> FavoriteEntity:
        """Convert SQLModel instance to domain entity."""
        return FavoriteEntity(
            id=self.id,
            user_id=self.user_id,
            movie_id=self.movie_id
        )


class Actor(SQLModel, table=True):
    """SQLModel table for actors."""

    __tablename__ = "actors"

    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    name: str
    bio: str

    def to_entity(self) -> ActorEntity:
        """Convert SQLModel instance to domain entity."""
        return ActorEntity(
            id=self.id,
            name=self.name,
            bio=self.bio
        )


class MovieActor(SQLModel, table=True):
    """SQLModel table for movie-actor relations."""

    __tablename__ = "movie_actors"

    id: Optional[int] = Field(default=None, primary_key=True, sa_column_kwargs={"autoincrement": True})
    movie_id: int = Field(foreign_key="movies.id", index=True)
    actor_id: int = Field(foreign_key="actors.id", index=True)

    def to_entity(self) -> MovieActorEntity:
        """Convert SQLModel instance to domain entity."""
        return MovieActorEntity(
            id=self.id,
            movie_id=self.movie_id,
            actor_id=self.actor_id
        )


