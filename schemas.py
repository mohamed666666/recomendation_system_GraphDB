from typing import Optional, List

from pydantic import BaseModel, ConfigDict


# Shared Pydantic config for ORM (SQLModel) compatibility
OrmConfig = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """Request body for creating a new user."""

    name: str
    email: str
    password: str


class UserUpdate(BaseModel):
    """Request body for updating an existing user (partial allowed)."""

    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserRead(BaseModel):
    """Response model representing a user."""

    model_config = OrmConfig

    id: int
    name: str
    email: str


class MovieCreate(BaseModel):
    """Request body for creating a new movie."""

    title: str
    description: str
    year: int
    genre: str
    actor_ids: List[int] = []


class MovieUpdate(BaseModel):
    """Request body for updating an existing movie (partial allowed)."""

    title: Optional[str] = None
    description: Optional[str] = None
    year: Optional[int] = None
    genre: Optional[str] = None


class MovieRead(BaseModel):
    """Response model representing a movie."""

    model_config = OrmConfig

    id: int
    title: str
    description: str
    year: int
    genre: str


class LikeCreate(BaseModel):
    """Request body for creating a like relation."""

    user_id: int
    movie_id: int


class LikeRead(BaseModel):
    """Response model representing a like relation."""

    model_config = OrmConfig

    id: int
    user_id: int
    movie_id: int


class RatingCreate(BaseModel):
    """Request body for creating a rating."""

    user_id: int
    movie_id: int
    rating: int


class RatingUpdate(BaseModel):
    """Request body for updating a rating (partial allowed)."""

    user_id: Optional[int] = None
    movie_id: Optional[int] = None
    rating: Optional[int] = None


class RatingRead(BaseModel):
    """Response model representing a rating."""

    model_config = OrmConfig

    id: int
    user_id: int
    movie_id: int
    rating: int


class WatchCreate(BaseModel):
    """Request body for creating a watch event."""

    user_id: int
    movie_id: int


class WatchRead(BaseModel):
    """Response model representing a watch event."""

    model_config = OrmConfig

    id: int
    user_id: int
    movie_id: int


class FavoriteCreate(BaseModel):
    """Request body for creating a favorite relation."""

    user_id: int
    movie_id: int


class FavoriteRead(BaseModel):
    """Response model representing a favorite relation."""

    model_config = OrmConfig

    id: int
    user_id: int
    movie_id: int


class ActorCreate(BaseModel):
    """Request body for creating an actor."""

    name: str
    bio: str


class ActorUpdate(BaseModel):
    """Request body for updating an actor (partial allowed)."""

    name: Optional[str] = None
    bio: Optional[str] = None


class ActorRead(BaseModel):
    """Response model representing an actor."""

    model_config = OrmConfig

    id: int
    name: str
    bio: str


class MovieActorCreate(BaseModel):
    """Request body for creating a movie-actor relation."""

    movie_id: int
    actor_id: int


class MovieActorRead(BaseModel):
    """Response model representing a movie-actor relation."""

    model_config = OrmConfig

    id: int
    movie_id: int
    actor_id: int


