# Movie Recommendation System with Graph Database

A hybrid recommendation system that combines a relational database (SQLite) for data persistence with a graph database (Neo4j) for efficient relationship-based recommendations. This architecture leverages the strengths of both database types: relational databases for structured data storage and graph databases for complex relationship queries.

## Architecture Overview

The system follows a **dual-database architecture** where:

- **SQLite (Relational DB)**: Acts as the source of truth, storing all entities and relationships in normalized tables
- **Neo4j (Graph DB)**: Mirrors the relational data as nodes and relationships, optimized for graph traversal and recommendation queries

### Data Flow

```
API Request → FastAPI Endpoint → Service Layer → Repository Layer
                                                    ↓
                                    ┌───────────────┴───────────────┐
                                    ↓                               ↓
                            Relational DB (SQLite)        Graph DB (Neo4j)
                            (Primary Storage)             (Recommendation Engine)
```

## System Components

### 1. **Entities** (`entities.py`)
Domain models representing core business objects:
- `User`: User accounts
- `Movie`: Movie information (title, description, year, genre)
- `Actor`: Actor information
- `like`: User likes on movies
- `rating`: User ratings for movies (1-5 scale)
- `watch`: Movies watched by users
- `favorite`: User's favorite movies
- `movieActors`: Many-to-many relationship between movies and actors

### 2. **Models** (`models.py`)
SQLModel table definitions that map to the relational database schema. Each model includes a `to_entity()` method to convert database records to domain entities.

### 3. **Repositories** (`repositories.py`)
Data access layer for the relational database:
- Handles CRUD operations using SQLModel
- Converts between database models and domain entities
- Examples: `UserRepository`, `MovieRepository`, `LikeRepository`, etc.

### 4. **Graph Repositories** (`graph_db.py`)
Neo4j operations for graph database:
- **Node Creation**: Creates/updates nodes (User, Movie, Actor) in Neo4j
- **Relationship Creation**: Creates relationships (LIKES, RATED, WATCHED, FAVORITED, ACTED_IN)
- **Recommendation Engine**: `MovieGraphRepository.recommend_movies()` - Core recommendation algorithm

### 5. **Services** (`services.py`)
Business logic layer that orchestrates operations:
- **Dual-Write Pattern**: When creating entities, writes to both relational and graph databases
- **Recommendation Service**: Uses graph database for recommendations, then fetches full movie details from relational DB

### 6. **Mappers** (`mappers.py`)
Converts between API schemas and domain entities:
- `to_entity()`: Converts API request schemas to domain entities
- `to_schema()`: Converts domain entities to API response schemas

### 7. **API Layer** (`main.py`)
FastAPI REST endpoints for:
- User management
- Movie CRUD operations
- Likes, ratings, watches, favorites
- **Recommendations**: `GET /users/{user_id}/recommendations`

## Data Mapping: Relational DB → Graph DB

### Node Mapping

When entities are created in the relational database, they are automatically mirrored to Neo4j:

#### Users
```python
# Relational DB: users table
# Graph DB: User node with properties {id, name, email}
MERGE (u:User {id: $id})
SET u.name = $name, u.email = $email
```

#### Movies
```python
# Relational DB: movies table
# Graph DB: Movie node with properties {id, title, description, year, genre}
MERGE (m:Movie {id: $id})
SET m.title = $title, m.description = $description, m.year = $year, m.genre = $genre
```

#### Actors
```python
# Relational DB: actors table
# Graph DB: Actor node with properties {id, name, bio}
MERGE (a:Actor {id: $id})
SET a.name = $name, a.bio = $bio
```

### Relationship Mapping

Junction tables in the relational database become relationships in the graph:

#### User-Movie Relationships

| Relational DB Table | Graph Relationship | Type |
|---------------------|-------------------|------|
| `likes` | `(User)-[:LIKES]->(Movie)` | Directed edge |
| `ratings` | `(User)-[:RATED {value: rating}]->(Movie)` | Directed edge with property |
| `watches` | `(User)-[:WATCHED]->(Movie)` | Directed edge |
| `favorites` | `(User)-[:FAVORITED]->(Movie)` | Directed edge |

#### Movie-Actor Relationships

| Relational DB Table | Graph Relationship | Type |
|---------------------|-------------------|------|
| `movie_actors` | `(Actor)-[:ACTED_IN]->(Movie)` | Directed edge |

### Example: Creating a Like

```python
# 1. API receives request
POST /likes
{
  "user_id": 1,
  "movie_id": 5
}

# 2. Service layer creates in relational DB
like_entity = LikeRepository.create(like(user_id=1, movie_id=5))
# → Inserts into SQLite 'likes' table

# 3. Service layer mirrors to graph DB
LikeGraphRepository.create_like(user_id=1, movie_id=5)
# → Creates relationship in Neo4j:
#    MERGE (u:User {id: 1})
#    MERGE (m:Movie {id: 5})
#    MERGE (u)-[:LIKES]->(m)
```

## Recommendation Algorithm

The recommendation system uses a **multi-strategy approach** with priority ordering:

### Strategy 1: Genre-Based Recommendations (Highest Priority)
Finds movies in the same genre as the user's liked movies.

```cypher
MATCH (u:User {id: $user_id})-[:LIKES]->(liked:Movie)
MATCH (rec:Movie)
WHERE rec.genre = liked.genre 
  AND NOT (u)-[:LIKES]->(rec)
  AND NOT (u)-[:WATCHED]->(rec)
WITH rec, COUNT(DISTINCT liked) as genre_match_score
ORDER BY genre_match_score DESC
RETURN DISTINCT rec.id as movie_id
```

**Scoring**: Movies matching multiple liked genres get higher scores.

### Strategy 2: Actor-Based Recommendations
Recommends movies featuring actors from the user's liked movies.

```cypher
MATCH (u:User {id: $user_id})-[:LIKES]->(liked:Movie)
      <-[:ACTED_IN]-(a:Actor)-[:ACTED_IN]->(rec:Movie)
WHERE NOT (u)-[:LIKES]->(rec)
  AND NOT (u)-[:WATCHED]->(rec)
WITH rec, COUNT(DISTINCT a) as actor_match_score
ORDER BY actor_match_score DESC
RETURN DISTINCT rec.id as movie_id
```

**Scoring**: Movies with more shared actors get higher scores.

### Strategy 3: Top-Rated Movies (Fallback)
Recommends highly-rated movies that the user hasn't interacted with.

```cypher
MATCH (m:Movie)<-[r:RATED]-(:User)
WITH m, AVG(r.value) AS avg_rating, COUNT(r) AS rating_count
WHERE avg_rating >= 4 AND rating_count >= 2
  AND NOT EXISTS { MATCH (:User {id: $user_id})-[:LIKES]->(m) }
  AND NOT EXISTS { MATCH (:User {id: $user_id})-[:WATCHED]->(m) }
ORDER BY avg_rating DESC, rating_count DESC
RETURN m.id AS movie_id
```

**Criteria**: Average rating ≥ 4.0 with at least 2 ratings.

### Strategy 4: User's Favorites
Includes movies the user has favorited but not yet watched.

```cypher
MATCH (u:User {id: $user_id})-[:FAVORITED]->(m:Movie)
WHERE NOT (u)-[:WATCHED]->(m)
RETURN DISTINCT m.id as movie_id
```

### Recommendation Aggregation

The system combines results from all strategies with deduplication:

1. **Priority Order**: Genre → Actors → Top Rated → Favorites
2. **Deduplication**: Each movie ID appears only once
3. **Limit**: Returns top N recommendations (default: 10)

```python
# Pseudocode
recommended = []
seen = set()

# Add genre-based (highest priority)
for movie_id in genre_recommendations:
    if movie_id not in seen:
        recommended.append(movie_id)
        seen.add(movie_id)

# Continue with other strategies if needed...
```

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users` | List all users |
| `POST` | `/users` | Create a new user |
| `GET` | `/movies` | List all movies |
| `GET` | `/movies/{id}` | Get movie by ID |
| `POST` | `/movies` | Create a new movie |
| `PUT` | `/movies/{id}` | Update a movie |
| `DELETE` | `/movies/{id}` | Delete a movie |
| `POST` | `/likes` | User likes a movie |
| `POST` | `/ratings` | User rates a movie |
| `POST` | `/favorites` | User favorites a movie |
| `GET` | `/actors` | List all actors |
| `POST` | `/actors` | Create an actor |

### Recommendation Endpoint

**`GET /users/{user_id}/recommendations`**

Returns personalized movie recommendations for a user.

**Response:**
```json
[
  {
    "id": 1,
    "title": "The Matrix",
    "description": "A computer hacker learns about the true nature of reality",
    "year": 1999,
    "genre": "Sci-Fi"
  },
  ...
]
```

**How it works:**
1. Calls `MovieGraphRepository.recommend_movies(user_id, limit=10)`
2. Executes Cypher queries in Neo4j to get movie IDs
3. Fetches full movie details from relational DB using the IDs
4. Returns complete movie objects

## Setup and Configuration

### Prerequisites

- Python 3.8+
- Neo4j Database (running locally or remotely)
- Required Python packages (see `requirements.txt` if available)

### Environment Variables

```bash
# Neo4j Configuration
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=123456789
```

### Database Setup

1. **Relational Database**: SQLite database (`app.db`) is created automatically on first run
2. **Graph Database**: Ensure Neo4j is running and accessible

### Running the Application

```bash
# Install dependencies
pip install fastapi uvicorn sqlmodel neo4j

# Run the server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Benefits of This Architecture

### 1. **Separation of Concerns**
- Relational DB: Reliable, ACID-compliant data storage
- Graph DB: Optimized for relationship queries

### 2. **Performance**
- Graph traversals in Neo4j are much faster than complex JOINs in SQL
- Recommendation queries can traverse multiple relationship hops efficiently

### 3. **Scalability**
- Can scale relational and graph databases independently
- Graph queries remain fast even with millions of relationships

### 4. **Flexibility**
- Easy to add new recommendation strategies by modifying Cypher queries
- Can experiment with different graph algorithms without affecting relational schema

## Data Consistency

The system maintains **eventual consistency** between databases:
- Writes go to relational DB first (source of truth)
- Graph DB is updated synchronously after successful relational write
- If graph write fails, relational data remains intact

**Note**: The system continues to function even if Neo4j is unavailable (recommendations will return empty).

## Future Enhancements

Potential improvements:
- **Collaborative Filtering**: Find users with similar preferences
- **Real-time Updates**: Event-driven graph synchronization
- **Graph Algorithms**: PageRank, community detection for recommendations
- **Caching**: Cache recommendation results for frequently accessed users
- **A/B Testing**: Test different recommendation strategies

## Project Structure

```
recomendation_system_GraphDB/
├── entities.py          # Domain entities
├── models.py            # SQLModel table definitions
├── repositories.py      # Relational DB repositories
├── graph_db.py          # Neo4j graph repositories
├── services.py          # Business logic layer
├── mappers.py           # Schema-entity mappers
├── schemas.py           # Pydantic schemas
├── interfaces.py        # Repository interfaces
├── main.py              # FastAPI application
├── seed.py              # Database seeding script
└── app.db               # SQLite database file
```

## License

[Add your license here]

