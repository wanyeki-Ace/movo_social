# Movo

A Twitter-like social media platform built with Django, demonstrating core **Data Structures and Algorithms** concepts.

## Quick Start

```bash
pip install -r requirements.txt
python manage.py makemigrations users
python manage.py makemigrations posts
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

Open http://127.0.0.1:8000 — log in with any seed user and password `password123`.

Seed users: `alice`, `bob`, `charlie`, `diana`, `eve`, `frank`, `nova`

---

## Deploying to Heroku

These instructions use the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli). Make sure you have it installed and are logged in (`heroku login`) before starting.

### Prerequisites

- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed
- A Heroku account
- Git repository initialised (already done if you cloned this project)

### Step 1 — Create a Heroku app

```bash
heroku create your-app-name
```

Replace `your-app-name` with a unique name. Heroku will also accept a randomly generated name if you omit it:

```bash
heroku create
```

### Step 2 — Add the Heroku Postgres add-on

Heroku Postgres is a free managed PostgreSQL service:

```bash
heroku addons:create heroku-postgresql:essential-0 --app your-app-name
```

This automatically sets the `DATABASE_URL` environment variable on your app, which Django picks up via `dj-database-url`.

### Step 3 — Set required environment variables

```bash
# Generate a strong secret key (run this in Python to produce one)
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Set it on Heroku
heroku config:set DJANGO_SECRET_KEY='<paste-generated-key-here>' --app your-app-name

# Disable debug mode in production
heroku config:set DEBUG=False --app your-app-name

# Allow requests to your Heroku domain
heroku config:set ALLOWED_HOSTS='your-app-name.herokuapp.com' --app your-app-name
```

### Step 3.5 — Add Cloudinary for persistent media storage

Heroku's filesystem is **ephemeral** — any file written to disk (uploaded photo, video, avatar) is lost the next time your dyno restarts. Cloudinary is the simplest fix: it stores all user-uploaded media in the cloud and serves them via its CDN.

**Add the free Cloudinary add-on:**

```bash
heroku addons:create cloudinary:starter --app your-app-name
```

This automatically sets the `CLOUDINARY_URL` environment variable on your Heroku app. Django will detect it and switch `DEFAULT_FILE_STORAGE` to `cloudinary_storage.storage.MediaCloudinaryStorage` — no code change required.

> **Already have a Cloudinary account?** Paste your URL directly instead:
>
> ```bash
> heroku config:set CLOUDINARY_URL='cloudinary://API_KEY:API_SECRET@CLOUD_NAME' --app your-app-name
> ```

**Local development** does *not* need Cloudinary. When `CLOUDINARY_URL` is unset the app falls back to Django's default local filesystem storage (`media/` directory), which works fine for local testing.

### Step 4 — Deploy the code

Push the `main` branch (or whichever branch you are on) to Heroku:

```bash
git push heroku main
```

If your working branch is not `main`, use:

```bash
git push heroku HEAD:main
```

### Step 5 — Post-deployment steps (automatic)

The `Procfile` `release` phase runs `python manage.py migrate --noinput` automatically every time you deploy. You do **not** need to run migrations manually.

If you want to seed the database with example users and posts, run:

```bash
heroku run python manage.py seed_data --app your-app-name
```

### Step 6 — Open the app

```bash
heroku open --app your-app-name
```

Log in with any seed user (e.g. `alice`) and password `password123`.

---

### Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes (auto-set by Heroku Postgres) | PostgreSQL connection URL |
| `DJANGO_SECRET_KEY` | Yes | Django secret key — keep this private |
| `DEBUG` | No (default: `False`) | Set to `True` only for local development |
| `ALLOWED_HOSTS` | Yes | Comma-separated list of allowed hostnames (e.g. `your-app-name.herokuapp.com`) |
| `CLOUDINARY_URL` | Yes (Heroku) / No (local) | Cloudinary connection URL — auto-set by the add-on. When present, all user-uploaded media is stored on Cloudinary instead of the local filesystem. |

---

### Useful Heroku CLI Commands

```bash
# View live application logs
heroku logs --tail --app your-app-name

# Run a one-off Django management command
heroku run python manage.py <command> --app your-app-name

# Open a Django shell on Heroku
heroku run python manage.py shell --app your-app-name

# List all config vars
heroku config --app your-app-name
```

---

## Screenshots

### Login

![Login page](https://github.com/user-attachments/assets/bd4e4ed2-1ec0-4781-8b93-aaf19e37056a)

### Feed

![Home feed](https://github.com/user-attachments/assets/c4e565f9-9762-44f3-8f19-27cfa87a6286)

### Trending (Explore)

![Explore / Trending page](https://github.com/user-attachments/assets/dd5f6f5a-03ec-4a2e-9fff-c3c47becdc38)

### Profile

![User profile page](https://github.com/user-attachments/assets/072d58f7-4301-4a30-bcb4-75ab4c174536)

### Post Detail

![Post detail with comments](https://github.com/user-attachments/assets/6785e853-c038-4045-af04-121ae936085e)

---

## System Design

```
Browser ──► Django Views ──► DSA Layer ──► PostgreSQL DB (Heroku) / SQLite (local)
              │
              ├── users app  (auth, profiles, follow)
              ├── posts app  (posts, likes, comments)
              ├── dsa module (Graph, MaxHeap, HashTable)
              └── media uploads ──► Cloudinary CDN (Heroku) / local media/ (local dev)
```

**Request lifecycle:**
1. Request hits Django URL router
2. View queries the database (ORM)
3. DSA structures process/rank the data
4. Rendered HTML is returned with Tailwind CSS styling

---

## Data Structures & Algorithms

### 1. Graph (`dsa/graph.py`)

**Structure:** Directed adjacency-list graph  
**Use case:** Modelling the social network (who follows whom)

Each user is a node; each follow relationship is a directed edge.  
Stored as `dict[int, set[int]]` — space-efficient for sparse graphs.

**Operations:** O(1) add_user, O(1) add_follow, O(V+E) BFS traversal

---

### 2. BFS Recommendations (`dsa/graph.py → bfs_recommendations`)

**Algorithm:** Breadth-First Search on the social graph  
**Use case:** "People You May Know" widget in the feed sidebar

Candidates are scored by how many Level-1 users also follow them (mutual connections).  
**Complexity:** O(V + E) — visits each node and edge at most once.

---

### 3. Max-Heap (`dsa/heap.py`)

**Structure:** Binary max-heap (array-based, from scratch)  
**Use case:** Trending posts on the Explore page

```
Engagement Score = likes + comments×2 + recency_bonus
recency_bonus    = max(0, 48 - hours_since_post) × 2
```

---

### 4. Hash Table (`dsa/hash_table.py`)

**Structure:** Hash table with separate chaining  
**Use case:** O(1) lookup of "did the current user like this post?"

**Hash function:** Polynomial rolling hash  
**Collision resolution:** Separate chaining  
**Auto-resize:** Doubles capacity when load factor exceeds 0.75

---

## Project Structure

```
movo/
├── movo_project/     # Django project settings & routing
├── users/            # User model, auth, profiles, follow
├── posts/            # Posts, likes, comments, trending
├── dsa/              # Pure DSA implementations
│   ├── graph.py      # Directed graph + BFS
│   ├── heap.py       # Binary max-heap
│   └── hash_table.py # Hash table with chaining
├── templates/        # Django HTML templates (Tailwind CSS)
├── static/           # CSS
└── media/            # User-uploaded files
```

---

## Tech Stack

| Layer      | Technology            |
|------------|----------------------|
| Backend    | Django 4.x (Python)  |
| Database   | PostgreSQL (Heroku) / SQLite (local) |
| Frontend   | Tailwind CSS (CDN)   |
| Images     | Pillow               |
| Media storage | Cloudinary (Heroku) / local filesystem (local dev) |
| DSA        | Pure Python          |

---

## Features

- User registration & authentication
- Post creation (text, images, videos)
  - Instant image thumbnail preview when selecting a photo
  - Video filename badge when selecting a video
  - Upload progress indicator — Post button shows "Uploading…" spinner while submitting
  - Deselect file with the ✕ clear button before posting
- Like & comment on posts
- Follow / unfollow users
- Personalised feed (posts from followed users)
- Trending explore page (Max-Heap ranking)
- BFS-powered "Who to Follow" recommendations
- Profile pages with stats
- Seed data with 7 example users including space & astronomy posts
- Persistent media storage via Cloudinary on Heroku (photos, videos, and avatars survive dyno restarts)
