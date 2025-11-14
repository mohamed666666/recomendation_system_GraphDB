import random
import time
from typing import Any, Dict, List, Tuple

import requests


BASE_URL = "http://127.0.0.1:8001"


def post(path: str, json: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to POST JSON and return parsed JSON, raising on HTTP errors."""
    resp = requests.post(f"{BASE_URL}{path}", json=json, timeout=15)
    resp.raise_for_status()
    return resp.json()


def get(path: str) -> List[Dict[str, Any]]:
    """Helper to GET and return parsed JSON."""
    resp = requests.get(f"{BASE_URL}{path}", timeout=15)
    resp.raise_for_status()
    return resp.json()


def seed_users() -> List[int]:
    """Create 5 users and return their ids."""
    names = [
        ("Alice Johnson", "alice@example.com"),
        ("Bob Smith", "bob@example.com"),
        ("Carol White", "carol@example.com"),
        ("David Lee", "david@example.com"),
        ("Eve Turner", "eve@example.com"),
    ]
    user_ids: List[int] = []
    for name, email in names:
        body = {"name": name, "email": email, "password": "Passw0rd!"}
        data = post("/users", body)
        user_ids.append(data["id"])
    return user_ids


def seed_actors(n: int = 20) -> List[int]:
    """Create n actors with generated bios and return their ids."""
    first_names = ["Liam", "Olivia", "Noah", "Emma", "Ava", "Isabella", "Mason", "Sophia", "Lucas", "Mia"]
    last_names = ["Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Jackson", "Harris"]
    actor_ids: List[int] = []
    for i in range(n):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        bio = f"{name} is known for versatile performances across genres. #{i+1}"
        data = post("/actors", {"name": name, "bio": bio})
        actor_ids.append(data["id"])
    return actor_ids


def seed_movies(actor_ids: List[int]) -> List[int]:
    """Create ~10 movies, each linked to 2-4 actors via actor_ids; return movie ids."""
    titles = [
        ("Eclipse of Fate", "A thriller that bends reality.", 2018, "Thriller"),
        ("Starlight Sonata", "A heartfelt journey among the stars.", 2020, "Drama"),
        ("Neon Horizon", "Cops and hackers in a neon city.", 2019, "Action"),
        ("Whispers in Rain", "Mystery unfolds in a rainy town.", 2017, "Mystery"),
        ("Crimson Orchard", "A family saga with dark secrets.", 2021, "Drama"),
        ("Quantum Skies", "Pilots test a quantum engine.", 2022, "Sci-Fi"),
        ("Silent Harbor", "A coastal village with a hidden past.", 2016, "Drama"),
        ("Iron Requiem", "A retired agent faces old enemies.", 2015, "Action"),
        ("Paper Bridges", "Childhood friends reconnect.", 2023, "Romance"),
        ("Winter Ember", "A heist during a snowstorm.", 2014, "Crime"),
    ]
    movie_ids: List[int] = []
    for title, desc, year, genre in titles:
        k = random.randint(2, 4)
        chosen_actors = random.sample(actor_ids, k)
        body = {
            "title": title,
            "description": desc,
            "year": year,
            "genre": genre,
            "actor_ids": chosen_actors,
        }
        data = post("/movies", body)
        movie_ids.append(data["id"])
    return movie_ids


def seed_relations(user_ids: List[int], movie_ids: List[int]) -> None:
    """Create likes, ratings, watches, and favorites across users and movies."""
    # Likes: each user likes 3-6 movies
    for uid in user_ids:
        for mid in random.sample(movie_ids, k=random.randint(3, 6)):
            post("/likes", {"user_id": uid, "movie_id": mid})

    # Ratings: each user rates 2-5 movies with realistic distribution
    for uid in user_ids:
        for mid in random.sample(movie_ids, k=random.randint(2, 5)):
            # Biased towards 3-5 stars
            rating_val = random.choices([2, 3, 4, 5], weights=[1, 3, 4, 5], k=1)[0]
            post("/ratings", {"user_id": uid, "movie_id": mid, "rating": rating_val})

    # Watches: each user watches 4-7 movies
    for uid in user_ids:
        for mid in random.sample(movie_ids, k=random.randint(4, 7)):
            post("/watches", {"user_id": uid, "movie_id": mid})

    # Favorites: each user favorites 1-2 movies they likely liked
    for uid in user_ids:
        fav_pool = random.sample(movie_ids, k=random.randint(1, 2))
        for mid in fav_pool:
            post("/favorites", {"user_id": uid, "movie_id": mid})


def main() -> None:
    """Seed endpoint-based data in a natural-looking distribution."""
    random.seed(int(time.time()))

    print("Seeding users...")
    user_ids = seed_users()
    print(f"Created users: {user_ids}")

    print("Seeding actors...")
    actor_ids = seed_actors(20)
    print(f"Created actors: {len(actor_ids)}")

    print("Seeding movies (with actor links)...")
    movie_ids = seed_movies(actor_ids)
    print(f"Created movies: {movie_ids}")

    print("Seeding relations (likes, ratings, watches, favorites)...")
    seed_relations(user_ids, movie_ids)
    print("Done.")


if __name__ == "__main__":
    main()


