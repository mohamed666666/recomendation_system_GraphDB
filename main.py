from contextlib import asynccontextmanager
from typing import AsyncGenerator, List, Optional
import os

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from neo4j import GraphDatabase

from repositories import (
    UserRepository, MovieRepository, LikeRepository, RatingRepository, WatchRepository, FavoriteRepository, ActorRepository, MovieActorRepository,
)
from services import (
    UserManager, MovieManager, LikeManager, RatingManager, WatchManager, FavoriteManager, ActorManager,
)
from mappers import (
    UserMapper, MovieMapper, LikeMapper, RatingMapper, WatchMapper, FavoriteMapper, ActorMapper,
)
from schemas import (
    UserCreate, UserUpdate, UserRead,
    MovieCreate, MovieUpdate, MovieRead,
    LikeCreate, LikeRead,
    RatingCreate, RatingUpdate, RatingRead,
    WatchCreate, WatchRead,
    FavoriteCreate, FavoriteRead,
    ActorCreate, ActorUpdate, ActorRead,
)
from entities import User as UserEntity, Movie as MovieEntity, like as LikeEntity, rating as RatingEntity, watch as WatchEntity, favorite as FavoriteEntity, Actor as ActorEntity
from graph_db import (
    UserGraphRepository,
    MovieGraphRepository,
    LikeGraphRepository,
    RatingGraphRepository,
    WatchGraphRepository,
    FavoriteGraphRepository,
    ActorGraphRepository,
)


DATABASE_URL = "sqlite+aiosqlite:///./app.db"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    app.state.engine = engine
    session = AsyncSession(engine)
    app.state.session = session
    # Setup Neo4j driver
    neo4j_uri = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "123456789")
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    try:
        driver.verify_connectivity()
    except Exception:
        pass  # Continue even if Neo4j is not available
    app.state.neo4j_driver = driver
    try:
        yield
    finally:
        await session.close()
        await engine.dispose()
        try:
            driver.close()
        except Exception:
            pass


app = FastAPI(lifespan=lifespan)

# Enable CORS for local development (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost",
        "http://127.0.0.1",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_session() -> AsyncSession:
    session: AsyncSession = app.state.session
    return session


def get_neo4j_driver():
    return app.state.neo4j_driver


def get_user_manager(session: AsyncSession = Depends(get_session)) -> UserManager:
    driver = get_neo4j_driver()
    return UserManager(UserRepository(session), UserGraphRepository(driver))


def get_movie_manager(session: AsyncSession = Depends(get_session)) -> MovieManager:
    driver = get_neo4j_driver()
    return MovieManager(
        MovieRepository(session),
        MovieGraphRepository(driver),
        actor_repository=ActorRepository(session),
        movie_actor_repository=MovieActorRepository(session),
        actor_graph_repository=ActorGraphRepository(driver),
    )


def get_like_manager(session: AsyncSession = Depends(get_session)) -> LikeManager:
    driver = get_neo4j_driver()
    return LikeManager(LikeRepository(session), LikeGraphRepository(driver))


def get_rating_manager(session: AsyncSession = Depends(get_session)) -> RatingManager:
    driver = get_neo4j_driver()
    return RatingManager(RatingRepository(session), RatingGraphRepository(driver))


def get_watch_manager(session: AsyncSession = Depends(get_session)) -> WatchManager:
    driver = get_neo4j_driver()
    return WatchManager(WatchRepository(session), WatchGraphRepository(driver))


def get_favorite_manager(session: AsyncSession = Depends(get_session)) -> FavoriteManager:
    driver = get_neo4j_driver()
    return FavoriteManager(FavoriteRepository(session), FavoriteGraphRepository(driver))


def get_actor_manager(session: AsyncSession = Depends(get_session)) -> ActorManager:
    driver = get_neo4j_driver()
    return ActorManager(ActorRepository(session), ActorGraphRepository(driver))


user_mapper = UserMapper()
movie_mapper = MovieMapper()
like_mapper = LikeMapper()
rating_mapper = RatingMapper()
watch_mapper = WatchMapper()
favorite_mapper = FavoriteMapper()
actor_mapper = ActorMapper()


# Users
@app.get("/users", response_model=List[UserRead])
async def list_users(manager: UserManager = Depends(get_user_manager)):
    items = await manager.get_all()
    return [user_mapper.to_schema(u) for u in items]




@app.post("/users", response_model=UserRead, status_code=201)
async def create_user(body: UserCreate, manager: UserManager = Depends(get_user_manager)):
    entity = user_mapper.to_entity(body)
    created = await manager.create(entity)
    return user_mapper.to_schema(created)


# Movies
@app.get("/movies", response_model=List[MovieRead])
async def list_movies(manager: MovieManager = Depends(get_movie_manager)):
    items = await manager.get_all()
    return [movie_mapper.to_schema(m) for m in items]


@app.get("/movies/{id}", response_model=MovieRead)
async def get_movie(id: int, manager: MovieManager = Depends(get_movie_manager)):
    obj = await manager.get_by_id(id)
    if not obj:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie_mapper.to_schema(obj)


@app.post("/movies", response_model=MovieRead, status_code=201)
async def create_movie(body: MovieCreate, manager: MovieManager = Depends(get_movie_manager)):
    entity = movie_mapper.to_entity(body)
    try:
        created = await manager.create(entity, actor_ids=body.actor_ids)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return movie_mapper.to_schema(created)


@app.put("/movies/{id}", response_model=MovieRead)
async def update_movie(id: int, body: MovieUpdate, manager: MovieManager = Depends(get_movie_manager)):
    current = await manager.get_by_id(id)
    if not current:
        raise HTTPException(status_code=404, detail="Movie not found")
    updated_entity = MovieEntity(
        id=id,
        title=body.title if body.title is not None else current.title,
        description=body.description if body.description is not None else current.description,
        year=body.year if body.year is not None else current.year,
        genre=body.genre if body.genre is not None else current.genre,
    )
    updated = await manager.update(updated_entity)
    return movie_mapper.to_schema(updated)


@app.delete("/movies/{id}", status_code=204)
async def delete_movie(id: int, manager: MovieManager = Depends(get_movie_manager)):
    await manager.delete(id)
    return JSONResponse(status_code=204, content=None)


@app.get("/users/{user_id}/recommendations", response_model=List[MovieRead])
async def get_recommendations(user_id: int, manager: MovieManager = Depends(get_movie_manager)):
    """Get movie recommendations for a user based on their likes, ratings, and preferences."""
    movies = await manager.recommend_for_user(user_id, limit=10)
    return [movie_mapper.to_schema(m) for m in movies]


# Likes
@app.get("/likes", response_model=List[LikeRead])
async def list_likes(manager: LikeManager = Depends(get_like_manager)):
    items = await manager.get_all()
    return [like_mapper.to_schema(x) for x in items]



@app.post("/likes", response_model=LikeRead, status_code=201)
async def create_like(body: LikeCreate, manager: LikeManager = Depends(get_like_manager)):
    entity = like_mapper.to_entity(body)
    created = await manager.create(entity)
    return like_mapper.to_schema(created)




@app.post("/ratings", response_model=RatingRead, status_code=201)
async def create_rating(body: RatingCreate, manager: RatingManager = Depends(get_rating_manager)):
    entity = rating_mapper.to_entity(body)
    created = await manager.create(entity)
    return rating_mapper.to_schema(created)



@app.post("/favorites", response_model=FavoriteRead, status_code=201)
async def create_favorite(body: FavoriteCreate, manager: FavoriteManager = Depends(get_favorite_manager)):
    entity = favorite_mapper.to_entity(body)
    created = await manager.create(entity)
    return favorite_mapper.to_schema(created)




# Actors
@app.get("/actors", response_model=List[ActorRead])
async def list_actors(manager: ActorManager = Depends(get_actor_manager)):
    items = await manager.get_all()
    return [actor_mapper.to_schema(x) for x in items]




@app.post("/actors", response_model=ActorRead, status_code=201)
async def create_actor(body: ActorCreate, manager: ActorManager = Depends(get_actor_manager)):
    entity = actor_mapper.to_entity(body)
    created = await manager.create(entity)
    return actor_mapper.to_schema(created)






"""
un needed endpoints 

@app.put("/users/{id}", response_model=UserRead)
async def update_user(id: int, body: UserUpdate, manager: UserManager = Depends(get_user_manager)):
    current = await manager.get_by_id(id)
    if not current:
        raise HTTPException(status_code=404, detail="User not found")
    updated_entity = UserEntity(
        id=id,
        name=body.name if body.name is not None else current.name,
        email=body.email if body.email is not None else current.email,
        password=body.password if body.password is not None else current.password,
    )
    updated = await manager.update(updated_entity)
    return user_mapper.to_schema(updated)


@app.delete("/users/{id}", status_code=204)
async def delete_user(id: int, manager: UserManager = Depends(get_user_manager)):
    await manager.delete(id)
    return JSONResponse(status_code=204, content=None)



@app.get("/likes/{id}", response_model=LikeRead)
async def get_like(id: int, manager: LikeManager = Depends(get_like_manager)):
    obj = await manager.get_by_id(id)
    if not obj:
        raise HTTPException(status_code=404, detail="Like not found")
    return like_mapper.to_schema(obj)
@app.delete("/likes/{id}", status_code=204)
async def delete_like(id: int, manager: LikeManager = Depends(get_like_manager)):
    await manager.delete(id)
    return JSONResponse(status_code=204, content=None)


# Ratings
@app.get("/ratings", response_model=List[RatingRead])
async def list_ratings(manager: RatingManager = Depends(get_rating_manager)):
    items = await manager.get_all()
    return [rating_mapper.to_schema(x) for x in items]


@app.get("/ratings/{id}", response_model=RatingRead)
async def get_rating(id: int, manager: RatingManager = Depends(get_rating_manager)):
    obj = await manager.get_by_id(id)
    if not obj:
        raise HTTPException(status_code=404, detail="Rating not found")
    return rating_mapper.to_schema(obj)


@app.put("/ratings/{id}", response_model=RatingRead)
async def update_rating(id: int, body: RatingUpdate, manager: RatingManager = Depends(get_rating_manager)):
    current = await manager.get_by_id(id)
    if not current:
        raise HTTPException(status_code=404, detail="Rating not found")
    updated_entity = RatingEntity(
        id=id,
        user_id=body.user_id if body.user_id is not None else current.user_id,
        movie_id=body.movie_id if body.movie_id is not None else current.movie_id,
        rating=body.rating if body.rating is not None else current.rating,
    )
    updated = await manager.update(updated_entity)
    return rating_mapper.to_schema(updated)


@app.delete("/ratings/{id}", status_code=204)
async def delete_rating(id: int, manager: RatingManager = Depends(get_rating_manager)):
    await manager.delete(id)
    return JSONResponse(status_code=204, content=None)




# Watches
@app.get("/watches", response_model=List[WatchRead])
async def list_watches(manager: WatchManager = Depends(get_watch_manager)):
    items = await manager.get_all()
    return [watch_mapper.to_schema(x) for x in items]


@app.get("/watches/{id}", response_model=WatchRead)
async def get_watch(id: int, manager: WatchManager = Depends(get_watch_manager)):
    obj = await manager.get_by_id(id)
    if not obj:
        raise HTTPException(status_code=404, detail="Watch not found")
    return watch_mapper.to_schema(obj)


@app.post("/watches", response_model=WatchRead, status_code=201)
async def create_watch(body: WatchCreate, manager: WatchManager = Depends(get_watch_manager)):
    entity = watch_mapper.to_entity(body)
    created = await manager.create(entity)
    return watch_mapper.to_schema(created)


@app.delete("/watches/{id}", status_code=204)
async def delete_watch(id: int, manager: WatchManager = Depends(get_watch_manager)):
    await manager.delete(id)
    return JSONResponse(status_code=204, content=None)

@app.delete("/favorites/{id}", status_code=204)
async def delete_favorite(id: int, manager: FavoriteManager = Depends(get_favorite_manager)):
    await manager.delete(id)
    return JSONResponse(status_code=204, content=None)
    
@app.get("/actors/{id}", response_model=ActorRead)
async def get_actor(id: int, manager: ActorManager = Depends(get_actor_manager)):
    obj = await manager.get_by_id(id)
    if not obj:
        raise HTTPException(status_code=404, detail="Actor not found")
    return actor_mapper.to_schema(obj)
@app.put("/actors/{id}", response_model=ActorRead)
async def update_actor(id: int, body: ActorUpdate, manager: ActorManager = Depends(get_actor_manager)):
    current = await manager.get_by_id(id)
    if not current:
        raise HTTPException(status_code=404, detail="Actor not found")
    updated_entity = ActorEntity(
        id=id,
        name=body.name if body.name is not None else current.name,
        bio=body.bio if body.bio is not None else current.bio,
    )
    updated = await manager.update(updated_entity)
    return actor_mapper.to_schema(updated)


@app.delete("/actors/{id}", status_code=204)
async def delete_actor(id: int, manager: ActorManager = Depends(get_actor_manager)):
    await manager.delete(id)
    return JSONResponse(status_code=204, content=None)



# Favorites
@app.get("/favorites", response_model=List[FavoriteRead])
async def list_favorites(manager: FavoriteManager = Depends(get_favorite_manager)):
    items = await manager.get_all()
    return [favorite_mapper.to_schema(x) for x in items]


@app.get("/favorites/{id}", response_model=FavoriteRead)
async def get_favorite(id: int, manager: FavoriteManager = Depends(get_favorite_manager)):
    obj = await manager.get_by_id(id)
    if not obj:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return favorite_mapper.to_schema(obj)


"""