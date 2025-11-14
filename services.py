from typing import List, Optional

from interfaces import (
    IUserRepository,
    IMovieRepository,
    ILikeRepository,
    IRatingRepository,
    IWatchRepository,
    IFavoriteRepository,
    IActorRepository,
    IMovieActorRepository,
)
from entities import User, Movie, like, rating, watch, favorite, Actor, movieActors
from graph_db import (
    UserGraphRepository,
    MovieGraphRepository,
    LikeGraphRepository,
    RatingGraphRepository,
    WatchGraphRepository,
    FavoriteGraphRepository,
    ActorGraphRepository,
)


class UserManager:
    """Service layer for `User` providing async CRUD operations."""

    def __init__(self, user_repository: IUserRepository, user_graph_repository: Optional[UserGraphRepository] = None):
        self.user_repository = user_repository
        self.user_graph_repository = user_graph_repository

    async def get_all(self) -> List[User]:
        """Return all users."""
        return await self.user_repository.get_all()

    async def get_by_id(self, id: int) -> Optional[User]:
        """Return a user by id if found, else None."""
        return await self.user_repository.get_by_id(id)

    async def create(self, user: User) -> User:
        """Create a new user and return it. Also mirrors to graph if configured."""
        created = await self.user_repository.create(user)
        print(f"Created user: {created}")
        if self.user_graph_repository:
            # Mirror in graph database
            print(f"Mirroring user {created.id} to graph database")
            self.user_graph_repository.create_user(created)
        
        return created

    async def update(self, user: User) -> Optional[User]:
        """Update an existing user by id and return the updated instance, or None if not found."""
        return await self.user_repository.update(user)

    async def delete(self, id: int) -> None:
        """Delete a user by id. No return value."""
        await self.user_repository.delete(id)


class MovieManager:
    """Service layer for `Movie` providing async CRUD operations."""

    def __init__(self, movie_repository: IMovieRepository, movie_graph_repository: Optional[MovieGraphRepository] = None,
                 actor_repository: Optional[IActorRepository] = None,
                 movie_actor_repository: Optional[IMovieActorRepository] = None,
                 actor_graph_repository: Optional[ActorGraphRepository] = None):
        self.movie_repository = movie_repository
        self.movie_graph_repository = movie_graph_repository
        self.actor_repository = actor_repository
        self.movie_actor_repository = movie_actor_repository
        self.actor_graph_repository = actor_graph_repository

    async def recommend_for_user(self, user_id: int, limit: int = 10) -> List[Movie]:
        """Get movie recommendations for a user based on their preferences."""
        if not self.movie_graph_repository:
            return []
        movie_ids = self.movie_graph_repository.recommend_movies(user_id, limit)
        movies = []
        for mid in movie_ids:
            movie = await self.movie_repository.get_by_id(mid)
            if movie:
                movies.append(movie)
        return movies

    async def get_all(self) -> List[Movie]:
        return await self.movie_repository.get_all()

    async def get_by_id(self, id: int) -> Optional[Movie]:
        return await self.movie_repository.get_by_id(id)

    async def create(self, movie: Movie, actor_ids: Optional[list[int]] = None) -> Movie:
        # Validate actor ids if provided
        if actor_ids:
            if not self.actor_repository:
                raise ValueError("Actor repository not configured")
            missing = []
            for aid in actor_ids:
                if await self.actor_repository.get_by_id(aid) is None:
                    missing.append(aid)
            if missing:
                raise ValueError(f"Actors not found: {missing}")

        created = await self.movie_repository.create(movie)

        # Mirror movie to graph
        if self.movie_graph_repository:
            self.movie_graph_repository.create_movie(created)

        # Create many-to-many records and graph edges
        if actor_ids and self.movie_actor_repository:
            for aid in actor_ids:
                await self.movie_actor_repository.create(movieActors(movie_id=created.id, actor_id=aid))
                if self.actor_graph_repository:
                    self.actor_graph_repository.create_movie_actor(movie_id=created.id, actor_id=aid)

        return created

    async def update(self, movie: Movie) -> Optional[Movie]:
        return await self.movie_repository.update(movie)

    async def delete(self, id: int) -> None:
        await self.movie_repository.delete(id)


class LikeManager:
    """Service layer for `like` providing async CRUD operations."""

    def __init__(self, like_repository: ILikeRepository, like_graph_repository: Optional[LikeGraphRepository] = None):
        self.like_repository = like_repository
        self.like_graph_repository = like_graph_repository

    async def get_all(self) -> List[like]:
        return await self.like_repository.get_all()

    async def get_by_id(self, id: int) -> Optional[like]:
        return await self.like_repository.get_by_id(id)

    async def create(self, l: like) -> like:
        created = await self.like_repository.create(l)
        if self.like_graph_repository:
            self.like_graph_repository.create_like(created.user_id, created.movie_id)
        return created

    async def update(self, l: like) -> Optional[like]:
        return await self.like_repository.update(l)

    async def delete(self, id: int) -> None:
        await self.like_repository.delete(id)


class RatingManager:
    """Service layer for `rating` providing async CRUD operations."""

    def __init__(self, rating_repository: IRatingRepository, rating_graph_repository: Optional[RatingGraphRepository] = None):
        self.rating_repository = rating_repository
        self.rating_graph_repository = rating_graph_repository

    async def get_all(self) -> List[rating]:
        return await self.rating_repository.get_all()

    async def get_by_id(self, id: int) -> Optional[rating]:
        return await self.rating_repository.get_by_id(id)

    async def create(self, r: rating) -> rating:
        created = await self.rating_repository.create(r)
        if self.rating_graph_repository:
            self.rating_graph_repository.create_rating(created.user_id, created.movie_id, created.rating)
        return created

    async def update(self, r: rating) -> Optional[rating]:
        return await self.rating_repository.update(r)

    async def delete(self, id: int) -> None:
        await self.rating_repository.delete(id)


class WatchManager:
    """Service layer for `watch` providing async CRUD operations."""

    def __init__(self, watch_repository: IWatchRepository, watch_graph_repository: Optional[WatchGraphRepository] = None):
        self.watch_repository = watch_repository
        self.watch_graph_repository = watch_graph_repository

    async def get_all(self) -> List[watch]:
        return await self.watch_repository.get_all()

    async def get_by_id(self, id: int) -> Optional[watch]:
        return await self.watch_repository.get_by_id(id)

    async def create(self, w: watch) -> watch:
        created = await self.watch_repository.create(w)
        if self.watch_graph_repository:
            self.watch_graph_repository.create_watch(created.user_id, created.movie_id)
        return created

    async def update(self, w: watch) -> Optional[watch]:
        return await self.watch_repository.update(w)

    async def delete(self, id: int) -> None:
        await self.watch_repository.delete(id)


class FavoriteManager:
    """Service layer for `favorite` providing async CRUD operations."""

    def __init__(self, favorite_repository: IFavoriteRepository, favorite_graph_repository: Optional[FavoriteGraphRepository] = None):
        self.favorite_repository = favorite_repository
        self.favorite_graph_repository = favorite_graph_repository

    async def get_all(self) -> List[favorite]:
        return await self.favorite_repository.get_all()

    async def get_by_id(self, id: int) -> Optional[favorite]:
        return await self.favorite_repository.get_by_id(id)

    async def create(self, f: favorite) -> favorite:
        created = await self.favorite_repository.create(f)
        if self.favorite_graph_repository:
            self.favorite_graph_repository.create_favorite(created.user_id, created.movie_id)
        return created

    async def update(self, f: favorite) -> Optional[favorite]:
        return await self.favorite_repository.update(f)

    async def delete(self, id: int) -> None:
        await self.favorite_repository.delete(id)


class ActorManager:
    """Service layer for `Actor` providing async CRUD operations."""

    def __init__(self, actor_repository: IActorRepository, actor_graph_repository: Optional[ActorGraphRepository] = None):
        self.actor_repository = actor_repository
        self.actor_graph_repository = actor_graph_repository

    async def get_all(self) -> List[Actor]:
        return await self.actor_repository.get_all()

    async def get_by_id(self, id: int) -> Optional[Actor]:
        return await self.actor_repository.get_by_id(id)

    async def create(self, actor: Actor) -> Actor:
        created = await self.actor_repository.create(actor)
        if self.actor_graph_repository:
            self.actor_graph_repository.create_actor(created)
        return created

    async def update(self, actor: Actor) -> Optional[Actor]:
        return await self.actor_repository.update(actor)

    async def delete(self, id: int) -> None:
        await self.actor_repository.delete(id)
    