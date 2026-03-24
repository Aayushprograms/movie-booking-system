import requests
from django.conf import settings
from movies.models import Movie, Language


def fetch_movies():

    api_key = settings.TMDB_API_KEY

    for page in range(1, 6):  # fetch 5 pages (100 movies)

        print(f"\nFetching page {page}...")

        url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&page={page}"

        response = requests.get(url)
        data = response.json()

        for item in data.get("results", []):

            language_name = item.get("original_language", "English")
            language, _ = Language.objects.get_or_create(name=language_name)

            poster_path = item.get("poster_path")
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""

            release_date = item.get("release_date") or "2000-01-01"

            # Avoid duplicates
            if Movie.objects.filter(title=item["title"]).exists():
                continue

            movie = Movie.objects.create(
                title=item["title"],
                rating=item.get("vote_average", 0),
                release_date=release_date,
                language=language,
                poster_url=poster_url,
            )

            print("Added:", movie.title)

    print("\n✅ Finished fetching movies!")