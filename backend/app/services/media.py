"""
Imoogle 5.0 Media Service
Music, Movies, Books recommendations and lookups.
Supports: Spotify, Genius, TMDB, Google Books
"""

import httpx
import base64
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from app.config import settings


@dataclass
class MusicResult:
    title: str
    artist: str
    album: str
    preview_url: Optional[str]
    spotify_url: Optional[str]
    cover_url: Optional[str]
    lyrics_url: Optional[str] = None


@dataclass
class MovieResult:
    title: str
    year: str
    overview: str
    rating: float
    poster_url: Optional[str]
    genres: List[str]
    tmdb_url: str


@dataclass
class BookResult:
    title: str
    authors: List[str]
    description: str
    cover_url: Optional[str]
    preview_url: Optional[str]
    rating: float
    page_count: int


class MediaService:
    """
    Media recommendation service with:
    1. Music: Spotify API + Genius for lyrics
    2. Movies: TMDB API
    3. Books: Google Books API
    """
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.spotify_token = None
        self.spotify_token_expires = 0
    
    async def close(self):
        await self.http_client.aclose()
    
    # ==================== SPOTIFY / MUSIC ====================
    
    async def _get_spotify_token(self) -> Optional[str]:
        """Get Spotify access token using client credentials."""
        import time
        
        if not settings.SPOTIFY_CLIENT_ID or not settings.SPOTIFY_CLIENT_SECRET:
            return None
        
        # Return cached token if valid
        if self.spotify_token and time.time() < self.spotify_token_expires:
            return self.spotify_token
        
        url = "https://accounts.spotify.com/api/token"
        
        auth_str = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
        auth_b64 = base64.b64encode(auth_str.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        
        data = {"grant_type": "client_credentials"}
        
        response = await self.http_client.post(url, headers=headers, data=data)
        response.raise_for_status()
        result = response.json()
        
        self.spotify_token = result["access_token"]
        self.spotify_token_expires = time.time() + result["expires_in"] - 60
        
        return self.spotify_token
    
    async def search_music(
        self,
        query: str,
        limit: int = 5,
    ) -> List[MusicResult]:
        """Search for music on Spotify."""
        token = await self._get_spotify_token()
        if not token:
            return []
        
        url = "https://api.spotify.com/v1/search"
        
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "q": query,
            "type": "track",
            "limit": limit,
        }
        
        response = await self.http_client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for track in data.get("tracks", {}).get("items", []):
            results.append(MusicResult(
                title=track["name"],
                artist=", ".join(a["name"] for a in track["artists"]),
                album=track["album"]["name"],
                preview_url=track.get("preview_url"),
                spotify_url=track["external_urls"]["spotify"],
                cover_url=track["album"]["images"][0]["url"] if track["album"]["images"] else None,
            ))
        
        return results
    
    async def get_lyrics(self, song: str, artist: str) -> Optional[str]:
        """Get lyrics from Genius."""
        if not settings.GENIUS_API_KEY:
            return None
        
        # Search for the song
        url = "https://api.genius.com/search"
        
        headers = {"Authorization": f"Bearer {settings.GENIUS_API_KEY}"}
        params = {"q": f"{song} {artist}"}
        
        response = await self.http_client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        hits = data.get("response", {}).get("hits", [])
        if hits:
            # Return the lyrics URL - actual scraping would require additional processing
            return hits[0]["result"]["url"]
        
        return None
    
    async def get_music_recommendations(
        self,
        seed_tracks: List[str] = None,
        seed_artists: List[str] = None,
        seed_genres: List[str] = None,
        limit: int = 5,
    ) -> List[MusicResult]:
        """Get music recommendations from Spotify."""
        token = await self._get_spotify_token()
        if not token:
            return []
        
        url = "https://api.spotify.com/v1/recommendations"
        
        headers = {"Authorization": f"Bearer {token}"}
        params = {"limit": limit}
        
        if seed_tracks:
            params["seed_tracks"] = ",".join(seed_tracks[:5])
        if seed_artists:
            params["seed_artists"] = ",".join(seed_artists[:5])
        if seed_genres:
            params["seed_genres"] = ",".join(seed_genres[:5])
        
        # Default to popular genres if no seeds
        if not any([seed_tracks, seed_artists, seed_genres]):
            params["seed_genres"] = "pop,afrobeats,hip-hop"
        
        response = await self.http_client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for track in data.get("tracks", []):
            results.append(MusicResult(
                title=track["name"],
                artist=", ".join(a["name"] for a in track["artists"]),
                album=track["album"]["name"],
                preview_url=track.get("preview_url"),
                spotify_url=track["external_urls"]["spotify"],
                cover_url=track["album"]["images"][0]["url"] if track["album"]["images"] else None,
            ))
        
        return results
    
    # ==================== TMDB / MOVIES ====================
    
    async def search_movies(
        self,
        query: str,
        limit: int = 5,
    ) -> List[MovieResult]:
        """Search for movies on TMDB."""
        if not settings.TMDB_API_KEY:
            return []
        
        url = "https://api.themoviedb.org/3/search/movie"
        
        params = {
            "api_key": settings.TMDB_API_KEY,
            "query": query,
            "include_adult": False,
        }
        
        response = await self.http_client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Get genre list for mapping
        genres = await self._get_movie_genres()
        
        results = []
        for movie in data.get("results", [])[:limit]:
            genre_names = [genres.get(g, "") for g in movie.get("genre_ids", [])]
            
            results.append(MovieResult(
                title=movie["title"],
                year=movie.get("release_date", "")[:4],
                overview=movie.get("overview", "")[:300],
                rating=movie.get("vote_average", 0),
                poster_url=f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None,
                genres=genre_names,
                tmdb_url=f"https://www.themoviedb.org/movie/{movie['id']}",
            ))
        
        return results
    
    async def _get_movie_genres(self) -> Dict[int, str]:
        """Get TMDB genre mapping."""
        url = "https://api.themoviedb.org/3/genre/movie/list"
        
        params = {"api_key": settings.TMDB_API_KEY}
        
        response = await self.http_client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        return {g["id"]: g["name"] for g in data.get("genres", [])}
    
    async def get_movie_recommendations(
        self,
        genre: str = None,
        limit: int = 5,
    ) -> List[MovieResult]:
        """Get trending or genre-specific movie recommendations."""
        if not settings.TMDB_API_KEY:
            return []
        
        # Use discover endpoint for recommendations
        url = "https://api.themoviedb.org/3/discover/movie"
        
        params = {
            "api_key": settings.TMDB_API_KEY,
            "sort_by": "popularity.desc",
            "include_adult": False,
            "vote_average.gte": 6.0,
        }
        
        if genre:
            # Map genre name to ID
            genre_map = {
                "action": 28, "comedy": 35, "drama": 18, "horror": 27,
                "romance": 10749, "thriller": 53, "sci-fi": 878,
                "animation": 16, "documentary": 99, "nollywood": 10749,
            }
            if genre.lower() in genre_map:
                params["with_genres"] = genre_map[genre.lower()]
        
        response = await self.http_client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        genres = await self._get_movie_genres()
        
        results = []
        for movie in data.get("results", [])[:limit]:
            genre_names = [genres.get(g, "") for g in movie.get("genre_ids", [])]
            
            results.append(MovieResult(
                title=movie["title"],
                year=movie.get("release_date", "")[:4],
                overview=movie.get("overview", "")[:300],
                rating=movie.get("vote_average", 0),
                poster_url=f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get("poster_path") else None,
                genres=genre_names,
                tmdb_url=f"https://www.themoviedb.org/movie/{movie['id']}",
            ))
        
        return results
    
    # ==================== GOOGLE BOOKS ====================
    
    async def search_books(
        self,
        query: str,
        limit: int = 5,
    ) -> List[BookResult]:
        """Search for books on Google Books."""
        url = "https://www.googleapis.com/books/v1/volumes"
        
        params = {
            "q": query,
            "maxResults": limit,
            "printType": "books",
        }
        
        if settings.GOOGLE_BOOKS_API_KEY:
            params["key"] = settings.GOOGLE_BOOKS_API_KEY
        
        response = await self.http_client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for book in data.get("items", []):
            info = book.get("volumeInfo", {})
            
            results.append(BookResult(
                title=info.get("title", "Unknown"),
                authors=info.get("authors", ["Unknown"]),
                description=info.get("description", "No description available")[:300],
                cover_url=info.get("imageLinks", {}).get("thumbnail"),
                preview_url=info.get("previewLink"),
                rating=info.get("averageRating", 0),
                page_count=info.get("pageCount", 0),
            ))
        
        return results
    
    async def get_book_recommendations(
        self,
        genre: str = None,
        limit: int = 5,
    ) -> List[BookResult]:
        """Get book recommendations by genre."""
        query = f"subject:{genre}" if genre else "bestseller"
        return await self.search_books(query, limit)
    
    # ==================== FORMATTING ====================
    
    def format_music_results(
        self,
        results: List[MusicResult],
        use_pidgin: bool = False,
    ) -> str:
        """Format music results for display."""
        if not results:
            if use_pidgin:
                return "Omo, I no fit find any song like that o. Try another one."
            return "I couldn't find any songs matching that. Try a different search."
        
        if use_pidgin:
            formatted = "See the music wey I find:\n\n"
        else:
            formatted = "Here are the songs I found:\n\n"
        
        for i, song in enumerate(results, 1):
            formatted += f"**{i}. {song.title}**\n"
            formatted += f"   Artist: {song.artist}\n"
            formatted += f"   Album: {song.album}\n"
            if song.spotify_url:
                formatted += f"   [Listen on Spotify]({song.spotify_url})\n"
            formatted += "\n"
        
        return formatted
    
    def format_movie_results(
        self,
        results: List[MovieResult],
        use_pidgin: bool = False,
    ) -> str:
        """Format movie results for display."""
        if not results:
            if use_pidgin:
                return "I no see any movie like that o. Try search something else."
            return "I couldn't find any movies matching that. Try a different search."
        
        if use_pidgin:
            formatted = "See movies wey I find:\n\n"
        else:
            formatted = "Here are the movies I found:\n\n"
        
        for i, movie in enumerate(results, 1):
            formatted += f"**{i}. {movie.title}** ({movie.year})\n"
            formatted += f"   Rating: {'⭐' * int(movie.rating / 2)} {movie.rating}/10\n"
            formatted += f"   Genres: {', '.join(movie.genres)}\n"
            formatted += f"   {movie.overview}...\n"
            formatted += f"   [View on TMDB]({movie.tmdb_url})\n\n"
        
        return formatted
    
    def format_book_results(
        self,
        results: List[BookResult],
        use_pidgin: bool = False,
    ) -> str:
        """Format book results for display."""
        if not results:
            if use_pidgin:
                return "I no fit find any book like that. Try another search."
            return "I couldn't find any books matching that. Try a different search."
        
        if use_pidgin:
            formatted = "See books wey I find for you:\n\n"
        else:
            formatted = "Here are the books I found:\n\n"
        
        for i, book in enumerate(results, 1):
            formatted += f"**{i}. {book.title}**\n"
            formatted += f"   By: {', '.join(book.authors)}\n"
            if book.rating:
                formatted += f"   Rating: {'⭐' * int(book.rating)} {book.rating}/5\n"
            if book.page_count:
                formatted += f"   Pages: {book.page_count}\n"
            formatted += f"   {book.description[:150]}...\n"
            if book.preview_url:
                formatted += f"   [Preview Book]({book.preview_url})\n"
            formatted += "\n"
        
        return formatted


# Singleton instance
media_service = MediaService()
