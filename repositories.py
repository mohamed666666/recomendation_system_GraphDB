from typing import List, Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import User as UserModel, Movie as MovieModel, Like as LikeModel, Rating as RatingModel, Watch as WatchModel, Favorite as FavoriteModel, Actor as ActorModel, MovieActor as MovieActorModel
from entities import User, Movie, like, rating, watch, favorite, Actor, movieActors
from interfaces import IUserRepository, IMovieRepository, ILikeRepository, IRatingRepository, IWatchRepository, IFavoriteRepository, IActorRepository, IMovieActorRepository


class UserRepository(IUserRepository):
    """Repository for `User` using SQLModel AsyncSession."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[User]:
        result = await self.db.exec(select(UserModel))
        models = result.all()
        return [model.to_entity() for model in models]

    async def get_by_id(self, id: int) -> Optional[User]:
        result = await self.db.exec(select(UserModel).where(UserModel.id == id))
        model = result.first()
        return model.to_entity() if model else None

    async def create(self, user: User) -> User:
        model = UserModel(name=user.name, email=user.email, password=user.password)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model.to_entity()

    async def update(self, user: User) -> Optional[User]:
        result = await self.db.exec(select(UserModel).where(UserModel.id == user.id))
        existing = result.first()
        if not existing:
            return None
        existing.name = user.name
        existing.email = user.email
        existing.password = user.password
        self.db.add(existing)
        await self.db.commit()
        await self.db.refresh(existing)
        return existing.to_entity()

    async def delete(self, id: int) -> None:
        result = await self.db.exec(select(UserModel).where(UserModel.id == id))
        model = result.first()
        if not model:
            return None
        await self.db.delete(model)
        await self.db.commit()
        return None


class MovieRepository(IMovieRepository):
    """Repository for `Movie` using SQLModel AsyncSession."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Movie]:
        result = await self.db.exec(select(MovieModel))
        models = result.all()
        return [model.to_entity() for model in models]

    async def get_by_id(self, id: int) -> Optional[Movie]:
        result = await self.db.exec(select(MovieModel).where(MovieModel.id == id))
        model = result.first()
        return model.to_entity() if model else None

    async def create(self, movie: Movie) -> Movie:
        model = MovieModel(title=movie.title, description=movie.description, year=movie.year, genre=movie.genre)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model.to_entity()

    async def update(self, movie: Movie) -> Optional[Movie]:
        result = await self.db.exec(select(MovieModel).where(MovieModel.id == movie.id))
        existing = result.first()
        if not existing:
            return None
        existing.title = movie.title
        existing.description = movie.description
        existing.year = movie.year
        existing.genre = movie.genre
        self.db.add(existing)
        await self.db.commit()
        await self.db.refresh(existing)
        return existing.to_entity()

    async def delete(self, id: int) -> None:
        result = await self.db.exec(select(MovieModel).where(MovieModel.id == id))
        model = result.first()
        if not model:
            return None
        await self.db.delete(model)
        await self.db.commit()
        return None


class LikeRepository(ILikeRepository):
    """Repository for `Like` using SQLModel AsyncSession."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[like]:
        result = await self.db.exec(select(LikeModel))
        models = result.all()
        return [model.to_entity() for model in models]

    async def get_by_id(self, id: int) -> Optional[like]:
        result = await self.db.exec(select(LikeModel).where(LikeModel.id == id))
        model = result.first()
        return model.to_entity() if model else None

    async def create(self, like_entity: like) -> like:
        model = LikeModel(user_id=like_entity.user_id, movie_id=like_entity.movie_id)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model.to_entity()

    async def update(self, like_entity: like) -> Optional[like]:
        result = await self.db.exec(select(LikeModel).where(LikeModel.id == like_entity.id))
        existing = result.first()
        if not existing:
            return None
        existing.user_id = like_entity.user_id
        existing.movie_id = like_entity.movie_id
        self.db.add(existing)
        await self.db.commit()
        await self.db.refresh(existing)
        return existing.to_entity()

    async def delete(self, id: int) -> None:
        result = await self.db.exec(select(LikeModel).where(LikeModel.id == id))
        model = result.first()
        if not model:
            return None
        await self.db.delete(model)
        await self.db.commit()
        return None


class RatingRepository(IRatingRepository):
    """Repository for `Rating` using SQLModel AsyncSession."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[rating]:
        result = await self.db.exec(select(RatingModel))
        models = result.all()
        return [model.to_entity() for model in models]

    async def get_by_id(self, id: int) -> Optional[rating]:
        result = await self.db.exec(select(RatingModel).where(RatingModel.id == id))
        model = result.first()
        return model.to_entity() if model else None

    async def create(self, rating_entity: rating) -> rating:
        model = RatingModel(user_id=rating_entity.user_id, movie_id=rating_entity.movie_id, rating=rating_entity.rating)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model.to_entity()

    async def update(self, rating_entity: rating) -> Optional[rating]:
        result = await self.db.exec(select(RatingModel).where(RatingModel.id == rating_entity.id))
        existing = result.first()
        if not existing:
            return None
        existing.user_id = rating_entity.user_id
        existing.movie_id = rating_entity.movie_id
        existing.rating = rating_entity.rating
        self.db.add(existing)
        await self.db.commit()
        await self.db.refresh(existing)
        return existing.to_entity()

    async def delete(self, id: int) -> None:
        result = await self.db.exec(select(RatingModel).where(RatingModel.id == id))
        model = result.first()
        if not model:
            return None
        await self.db.delete(model)
        await self.db.commit()
        return None


class WatchRepository(IWatchRepository):
    """Repository for `Watch` using SQLModel AsyncSession."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[watch]:
        result = await self.db.exec(select(WatchModel))
        models = result.all()
        return [model.to_entity() for model in models]

    async def get_by_id(self, id: int) -> Optional[watch]:
        result = await self.db.exec(select(WatchModel).where(WatchModel.id == id))
        model = result.first()
        return model.to_entity() if model else None

    async def create(self, watch_entity: watch) -> watch:
        model = WatchModel(user_id=watch_entity.user_id, movie_id=watch_entity.movie_id)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model.to_entity()

    async def update(self, watch_entity: watch) -> Optional[watch]:
        result = await self.db.exec(select(WatchModel).where(WatchModel.id == watch_entity.id))
        existing = result.first()
        if not existing:
            return None
        existing.user_id = watch_entity.user_id
        existing.movie_id = watch_entity.movie_id
        self.db.add(existing)
        await self.db.commit()
        await self.db.refresh(existing)
        return existing.to_entity()

    async def delete(self, id: int) -> None:
        result = await self.db.exec(select(WatchModel).where(WatchModel.id == id))
        model = result.first()
        if not model:
            return None
        await self.db.delete(model)
        await self.db.commit()
        return None


class FavoriteRepository(IFavoriteRepository):
    """Repository for `Favorite` using SQLModel AsyncSession."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[favorite]:
        result = await self.db.exec(select(FavoriteModel))
        models = result.all()
        return [model.to_entity() for model in models]

    async def get_by_id(self, id: int) -> Optional[favorite]:
        result = await self.db.exec(select(FavoriteModel).where(FavoriteModel.id == id))
        model = result.first()
        return model.to_entity() if model else None

    async def create(self, favorite_entity: favorite) -> favorite:
        model = FavoriteModel(user_id=favorite_entity.user_id, movie_id=favorite_entity.movie_id)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model.to_entity()

    async def update(self, favorite_entity: favorite) -> Optional[favorite]:
        result = await self.db.exec(select(FavoriteModel).where(FavoriteModel.id == favorite_entity.id))
        existing = result.first()
        if not existing:
            return None
        existing.user_id = favorite_entity.user_id
        existing.movie_id = favorite_entity.movie_id
        self.db.add(existing)
        await self.db.commit()
        await self.db.refresh(existing)
        return existing.to_entity()

    async def delete(self, id: int) -> None:
        result = await self.db.exec(select(FavoriteModel).where(FavoriteModel.id == id))
        model = result.first()
        if not model:
            return None
        await self.db.delete(model)
        await self.db.commit()
        return None


class ActorRepository(IActorRepository):
    """Repository for `Actor` using SQLModel AsyncSession."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[Actor]:
        result = await self.db.exec(select(ActorModel))
        models = result.all()
        return [model.to_entity() for model in models]

    async def get_by_id(self, id: int) -> Optional[Actor]:
        result = await self.db.exec(select(ActorModel).where(ActorModel.id == id))
        model = result.first()
        return model.to_entity() if model else None

    async def create(self, actor: Actor) -> Actor:
        model = ActorModel(name=actor.name, bio=actor.bio)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model.to_entity()

    async def update(self, actor: Actor) -> Optional[Actor]:
        result = await self.db.exec(select(ActorModel).where(ActorModel.id == actor.id))
        existing = result.first()
        if not existing:
            return None
        existing.name = actor.name
        existing.bio = actor.bio
        self.db.add(existing)
        await self.db.commit()
        await self.db.refresh(existing)
        return existing.to_entity()

    async def delete(self, id: int) -> None:
        result = await self.db.exec(select(ActorModel).where(ActorModel.id == id))
        model = result.first()
        if not model:
            return None
        await self.db.delete(model)
        await self.db.commit()
        return None


class MovieActorRepository(IMovieActorRepository):
    """Repository for `movieActors` using SQLModel AsyncSession."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[movieActors]:
        result = await self.db.exec(select(MovieActorModel))
        models = result.all()
        return [model.to_entity() for model in models]

    async def get_by_id(self, id: int) -> Optional[movieActors]:
        result = await self.db.exec(select(MovieActorModel).where(MovieActorModel.id == id))
        model = result.first()
        return model.to_entity() if model else None

    async def create(self, movie_actor: movieActors) -> movieActors:
        model = MovieActorModel(movie_id=movie_actor.movie_id, actor_id=movie_actor.actor_id)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return model.to_entity()

    async def update(self, movie_actor: movieActors) -> Optional[movieActors]:
        result = await self.db.exec(select(MovieActorModel).where(MovieActorModel.id == movie_actor.id))
        existing = result.first()
        if not existing:
            return None
        existing.movie_id = movie_actor.movie_id
        existing.actor_id = movie_actor.actor_id
        self.db.add(existing)
        await self.db.commit()
        await self.db.refresh(existing)
        return existing.to_entity()

    async def delete(self, id: int) -> None:
        result = await self.db.exec(select(MovieActorModel).where(MovieActorModel.id == id))
        model = result.first()
        if not model:
            return None
        await self.db.delete(model)
        await self.db.commit()
        return None


