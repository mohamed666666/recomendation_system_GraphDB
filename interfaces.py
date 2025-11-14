from entities import User, Movie, like, rating, watch, favorite, Actor, movieActors 
from typing import List, Optional
from abc import ABC, abstractmethod

class IUserRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[User]:
        pass
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[User]:
        pass
    @abstractmethod
    async def create(self, user: User) -> User:
        pass
    @abstractmethod
    async def update(self, user: User) -> User:
        pass
    @abstractmethod
    async def delete(self, id: int) -> None:
        pass


class IMovieRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[Movie]:
        pass
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Movie]:
        pass
    @abstractmethod
    async def create(self, movie: Movie) -> Movie:
        pass
    @abstractmethod
    async def update(self, movie: Movie) -> Movie:      
        pass
    @abstractmethod
    async def delete(self, id: int) -> None:
        """Delete a movie by its id."""
        pass

class ILikeRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[like]:
        pass
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[like]:
        pass
    @abstractmethod
    async def create(self, like: like) -> like:
        pass
    @abstractmethod
    async def update(self, like: like) -> like: 
        pass
    @abstractmethod
    async def delete(self, id: int) -> None:
        pass

class IRatingRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[rating]:
        pass
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[rating]:
        pass
    @abstractmethod
    async def create(self, rating: rating) -> rating:       
        pass
    @abstractmethod
    async def update(self, rating: rating) -> rating: 
        pass
    @abstractmethod
    async def delete(self, id: int) -> None:
        pass

class IWatchRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[watch]:
        pass
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[watch]:
        pass
    @abstractmethod
    async def create(self, watch: watch) -> watch:
        pass
    @abstractmethod
    async def update(self, watch: watch) -> watch:
        pass
    @abstractmethod
    async def delete(self, id: int) -> None:
        """Delete a watch record by its id."""
        pass
   

class IFavoriteRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[favorite]:
        pass
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[favorite]:
        pass
    @abstractmethod
    async def create(self, favorite: favorite) -> favorite:
        pass
    @abstractmethod
    async def update(self, favorite: favorite) -> favorite:
        pass
    @abstractmethod
    async def delete(self, id: int) -> None:
        """Delete a favorite record by its id."""
        pass

class IActorRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[Actor]:
        pass
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[Actor]:
        pass
    @abstractmethod
    async def create(self, actor: Actor) -> Actor:
        pass
    @abstractmethod
    async def update(self, actor: Actor) -> Actor:
        pass
    @abstractmethod
    async def delete(self, id: int) -> None:
        pass


class IMovieActorRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[movieActors]:
        pass
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[movieActors]:
        pass
    @abstractmethod
    async def create(self, movie_actor: movieActors) -> movieActors:
        pass
    @abstractmethod
    async def update(self, movie_actor: movieActors) -> movieActors:
        pass
    @abstractmethod
    async def delete(self, id: int) -> None:
        """Delete a movie actor relation by its id."""
        pass

