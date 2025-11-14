from typing import Optional

from neo4j import GraphDatabase, Driver

from entities import User as UserEntity, Movie as MovieEntity, Actor as ActorEntity
from typing import List

class _BaseGraphRepository:
    """Base class holding a Neo4j Driver instance."""

    def __init__(self, driver: Driver):
        self._driver = driver


class UserGraphRepository(_BaseGraphRepository):
    def __init__(self, driver: Driver):
        super().__init__(driver)

    def create_user(self, user: UserEntity) -> None:
        """Create or update a User node."""
        cypher = (
            "MERGE (u:User {id: $id}) "
            "SET u.name = $name, u.email = $email"
        )
        with self._driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(cypher, id=user.id, name=user.name, email=user.email)
            )


class MovieGraphRepository(_BaseGraphRepository):
    def __init__(self, driver: Driver):
        super().__init__(driver)

    def create_movie(self, movie: MovieEntity) -> None:
        """Create or update a Movie node."""
        cypher = (
            "MERGE (m:Movie {id: $id}) "
            "SET m.title = $title, m.description = $description, m.year = $year, m.genre = $genre"
        )
        with self._driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(
                    cypher,
                    id=movie.id,
                    title=movie.title,
                    description=movie.description,
                    year=movie.year,
                    genre=movie.genre,
                )
            )

    def recommend_movies(self, user_id: int, limit: int = 10) -> List[int]:
        """Recommend movies to a user based on:
        1. Same genre as user's liked movies
        2. Movies with actors from user's liked movies
        3. Top rated movies (fallback)
        4. User's favorited movies
        
        Returns list of movie IDs ordered by recommendation priority.
        """
        with self._driver.session() as session:
            # Priority 1: Movies with same genre as user's liked movies
            cypher_genre = """
                MATCH (u:User {id: $user_id})-[:LIKES]->(liked:Movie)
                MATCH (rec:Movie)
                WHERE rec.genre = liked.genre 
                  AND NOT (u)-[:LIKES]->(rec)
                  AND NOT (u)-[:WATCHED]->(rec)
                WITH rec, COUNT(DISTINCT liked) as genre_match_score
                ORDER BY genre_match_score DESC
                RETURN DISTINCT rec.id as movie_id, genre_match_score as score
                LIMIT $limit
            """
            genre_movies = session.execute_read(
                lambda tx: [record.data() for record in tx.run(cypher_genre, user_id=user_id, limit=limit * 2)]
            )
            genre_ids = {record["movie_id"]: record["score"] for record in genre_movies}
            
            # Priority 2: Movies with actors from user's liked movies
            cypher_actors = """
                MATCH (u:User {id: $user_id})-[:LIKES]->(liked:Movie)<-[:ACTED_IN]-(a:Actor)-[:ACTED_IN]->(rec:Movie)
                WHERE NOT (u)-[:LIKES]->(rec)
                  AND NOT (u)-[:WATCHED]->(rec)
                WITH rec, COUNT(DISTINCT a) as actor_match_score
                ORDER BY actor_match_score DESC
                RETURN DISTINCT rec.id as movie_id, actor_match_score as score
                LIMIT $limit
            """
            actor_movies = session.execute_read(
                lambda tx: [record.data() for record in tx.run(cypher_actors, user_id=user_id, limit=limit * 2)]
            )
            actor_ids = {record["movie_id"]: record["score"] for record in actor_movies}
            
            # Priority 3: Top rated movies (average rating >= 4)
            cypher_top_rated = """
                MATCH (m:Movie)<-[r:RATED]-(:User)
                WITH m, AVG(r.value) AS avg_rating, COUNT(r) AS rating_count
                WHERE avg_rating >= 4 AND rating_count >= 2
                  AND NOT EXISTS { MATCH (:User {id: $user_id})-[:LIKES]->(m) }
                  AND NOT EXISTS { MATCH (:User {id: $user_id})-[:WATCHED]->(m) }
                WITH DISTINCT m.id AS movie_id, avg_rating, rating_count
                ORDER BY avg_rating DESC, rating_count DESC
                RETURN movie_id, avg_rating AS score
                LIMIT $limit
            """
            top_rated = session.execute_read(
                lambda tx: [record.data() for record in tx.run(cypher_top_rated, user_id=user_id, limit=limit)]
            )
            top_rated_ids = {record["movie_id"]: record["score"] for record in top_rated}
            
            # Priority 4: User's favorited movies (if not already included)
            cypher_favorites = """
                MATCH (u:User {id: $user_id})-[:FAVORITED]->(m:Movie)
                WHERE NOT (u)-[:WATCHED]->(m)
                RETURN DISTINCT m.id as movie_id
                LIMIT $limit
            """
            favorites = session.execute_read(
                lambda tx: [record.data() for record in tx.run(cypher_favorites, user_id=user_id, limit=limit)]
            )
            favorite_ids = {record["movie_id"]: 1.0 for record in favorites}
            
            # Combine and deduplicate, maintaining priority order
            recommended = []
            seen = set()
            
            # Add genre-based recommendations first
            for mid, score in sorted(genre_ids.items(), key=lambda x: x[1], reverse=True):
                if mid not in seen:
                    recommended.append(mid)
                    seen.add(mid)
                    if len(recommended) >= limit:
                        break
            
            # Add actor-based recommendations
            if len(recommended) < limit:
                for mid, score in sorted(actor_ids.items(), key=lambda x: x[1], reverse=True):
                    if mid not in seen:
                        recommended.append(mid)
                        seen.add(mid)
                        if len(recommended) >= limit:
                            break
            
            # Add top rated movies
            if len(recommended) < limit:
                for mid, score in sorted(top_rated_ids.items(), key=lambda x: x[1], reverse=True):
                    if mid not in seen:
                        recommended.append(mid)
                        seen.add(mid)
                        if len(recommended) >= limit:
                            break
            
            # Add favorited movies
            if len(recommended) < limit:
                for mid in favorite_ids.keys():
                    if mid not in seen:
                        recommended.append(mid)
                        seen.add(mid)
                        if len(recommended) >= limit:
                            break
            
            return recommended


class LikeGraphRepository(_BaseGraphRepository):
    def __init__(self, driver: Driver):
        super().__init__(driver)

    def create_like(self, user_id: int, movie_id: int) -> None:
        """Create a LIKES relationship between User and Movie."""
        cypher = (
            "MERGE (u:User {id: $user_id}) "
            "MERGE (m:Movie {id: $movie_id}) "
            "MERGE (u)-[:LIKES]->(m)"
        )
        with self._driver.session() as session:
            session.execute_write(lambda tx: tx.run(cypher, user_id=user_id, movie_id=movie_id))


class RatingGraphRepository(_BaseGraphRepository):
    def __init__(self, driver: Driver):
        super().__init__(driver)

    def create_rating(self, user_id: int, movie_id: int, rating: int) -> None:
        """Create a RATED relationship between User and Movie with a rating property."""
        cypher = (
            "MERGE (u:User {id: $user_id}) "
            "MERGE (m:Movie {id: $movie_id}) "
            "MERGE (u)-[r:RATED]->(m) "
            "SET r.value = $rating"
        )
        with self._driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(cypher, user_id=user_id, movie_id=movie_id, rating=rating)
            )


class WatchGraphRepository(_BaseGraphRepository):
    def __init__(self, driver: Driver):
        super().__init__(driver)

    def create_watch(self, user_id: int, movie_id: int) -> None:
        """Create a WATCHED relationship between User and Movie."""
        cypher = (
            "MERGE (u:User {id: $user_id}) "
            "MERGE (m:Movie {id: $movie_id}) "
            "MERGE (u)-[:WATCHED]->(m)"
        )
        with self._driver.session() as session:
            session.execute_write(lambda tx: tx.run(cypher, user_id=user_id, movie_id=movie_id))


class FavoriteGraphRepository(_BaseGraphRepository):
    def __init__(self, driver: Driver):
        super().__init__(driver)

    def create_favorite(self, user_id: int, movie_id: int) -> None:
        """Create a FAVORITED relationship between User and Movie."""
        cypher = (
            "MERGE (u:User {id: $user_id}) "
            "MERGE (m:Movie {id: $movie_id}) "
            "MERGE (u)-[:FAVORITED]->(m)"
        )
        with self._driver.session() as session:
            session.execute_write(lambda tx: tx.run(cypher, user_id=user_id, movie_id=movie_id))


class ActorGraphRepository(_BaseGraphRepository):
    def __init__(self, driver: Driver):
        super().__init__(driver)

    def create_actor(self, actor: ActorEntity) -> None:
        """Create or update an Actor node."""
        cypher = (
            "MERGE (a:Actor {id: $id}) "
            "SET a.name = $name, a.bio = $bio"
        )
        with self._driver.session() as session:
            session.execute_write(
                lambda tx: tx.run(cypher, id=actor.id, name=actor.name, bio=actor.bio)
            )

    def create_movie_actor(self, movie_id: int, actor_id: int) -> None:
        """Create an ACTED_IN relationship between Actor and Movie."""
        cypher = (
            "MERGE (a:Actor {id: $actor_id}) "
            "MERGE (m:Movie {id: $movie_id}) "
            "MERGE (a)-[:ACTED_IN]->(m)"
        )
        with self._driver.session() as session:
            session.execute_write(lambda tx: tx.run(cypher, actor_id=actor_id, mo vie_id=movie_id))

         