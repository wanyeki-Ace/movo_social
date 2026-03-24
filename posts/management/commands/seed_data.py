"""
Management command to seed Movo with example users and posts.

Run with: python manage.py seed_data

Creates 6 users (alice, bob, charlie, diana, eve, frank) with password 'password123',
follow relationships forming a social graph, and varied posts.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from users.models import User, Follow
from posts.models import Post, Like, Comment


USERS = [
    {
        'username': 'alice',
        'email': 'alice@example.com',
        'bio': 'Software engineer and coffee enthusiast. Building the future one commit at a time.',
        'website': 'https://alice.dev',
        'first_name': 'Alice',
        'last_name': 'Anderson',
    },
    {
        'username': 'bob',
        'email': 'bob@example.com',
        'bio': 'Photographer | Traveller | Part-time philosopher. Life is too short for bad coffee.',
        'website': '',
        'first_name': 'Bob',
        'last_name': 'Baker',
    },
    {
        'username': 'charlie',
        'email': 'charlie@example.com',
        'bio': 'Musician by night, data scientist by day. Fan of DSA and lo-fi beats.',
        'website': 'https://charlie.music',
        'first_name': 'Charlie',
        'last_name': 'Chen',
    },
    {
        'username': 'diana',
        'email': 'diana@example.com',
        'bio': 'ML researcher. Teaching machines to think since 2018. She/Her.',
        'website': 'https://diana.ai',
        'first_name': 'Diana',
        'last_name': 'Davis',
    },
    {
        'username': 'eve',
        'email': 'eve@example.com',
        'bio': 'Open-source advocate. If it\'s not on GitHub, does it even exist?',
        'website': 'https://github.com/eve',
        'first_name': 'Eve',
        'last_name': 'Evans',
    },
    {
        'username': 'frank',
        'email': 'frank@example.com',
        'bio': 'Barista turned backend dev. My code runs on caffeine and recursion.',
        'website': '',
        'first_name': 'Frank',
        'last_name': 'Foster',
    },
    {
        'username': 'nova',
        'email': 'nova@example.com',
        'bio': 'Astrophysicist and science communicator. The universe is under no obligation to make sense to you.',
        'website': 'https://nova.space',
        'first_name': 'Nova',
        'last_name': 'Nakamura',
    },
]

POSTS = [
    # alice
    ('alice', "Just pushed a new feature that uses BFS to find the shortest path through my to-do list. Works great, but now I have 0 items left."),
    ('alice', "Hot take: a well-designed hash table is a work of art. O(1) average lookup? Chef's kiss."),
    ('alice', "Morning standup: 'I am blocked.' Translation: I spent 3 hours debugging a missing semicolon. #DevLife"),
    ('alice', "Graph theory is everywhere once you start looking. Social networks, maps, even recipe dependencies. Mind blown."),
    ('alice', "Space fact of the day: the Milky Way and Andromeda galaxies are on a collision course, but don't worry — it won't happen for about 4.5 billion years."),
    # bob
    ('bob', "Sunrise from the mountain top this morning. Worth every step. #Photography #Nature"),
    ('bob', "Tried to explain recursion to my cat. She just stared at me, walked away, and knocked my coffee off the table. Fair."),
    ('bob', "Road trip playlist: 47 songs, all bangers. The algorithm finally got me."),
    ('bob', "Life advice: always carry a camera, always carry snacks. You'll thank me later."),
    # charlie
    ('charlie', "DSA hot take: sorting algorithms are just music — QuickSort is jazz (fast and chaotic), MergeSort is classical (structured and reliable)."),
    ('charlie', "Wrote a Max-Heap implementation from scratch today. There's something deeply satisfying about watching the heap property hold."),
    ('charlie', "New band name idea: Null Pointer Exception. We only play stack overflow shows."),
    ('charlie', "Adjacency lists > adjacency matrices for sparse graphs. Fight me. (Please don't, I'm fragile.)"),
    # diana
    ('diana', "Gradient descent is just a fancy way of saying 'roll downhill until you find something good.' Neural nets in a nutshell."),
    ('diana', "Just submitted my paper on graph-based recommendation systems. 6 months of work, 8 pages. Worth it."),
    ('diana', "Reminder: correlation does not imply causation. Ice cream sales and drowning rates both spike in summer. Stay critical."),
    ('diana', "The best model is the one that ships. Perfect is the enemy of done. #MLOps"),
    # eve
    ('eve', "Opened my first PR at age 16. Today I merged my 1000th. Open source changed my life."),
    ('eve', "If your README is longer than your codebase, you might be doing it right. Documentation matters, people!"),
    ('eve', "Hot reload, hot coffee, hot takes. That's my stack."),
    ('eve', "Spent 4 hours on a bug. Turned out to be a timezone issue. It's ALWAYS a timezone issue."),
    # frank
    ('frank', "Pulled a double shot, wrote a binary search, called it a day. Productive? Absolutely."),
    ('frank', "My latte art game and my code quality are both improving. Slowly. But surely."),
    ('frank', "Recursion joke: to understand recursion, you must first understand recursion."),
    ('frank', "Stack-based undo/redo in text editors — one of the most elegant real-world DSA applications. Change my mind."),
    # nova — space & astronomy posts
    ('nova', "The James Webb Space Telescope just released new infrared images of the Pillars of Creation. Every pixel is a star or a galaxy. The scale is genuinely incomprehensible."),
    ('nova', "Black holes do not 'suck' things in — they simply have gravity, same as any other mass. The difference is what happens when you get too close to the event horizon."),
    ('nova', "Fun fact: a neutron star is so dense that a teaspoon of its material would weigh about a billion tonnes on Earth. Nuclear pasta is the strongest known material in the universe."),
    ('nova', "The Voyager 1 probe launched in 1977 and is now over 23 billion km from Earth — still sending data. Human ingenuity at its finest."),
    ('nova', "Mars once had a thicker atmosphere and liquid water on its surface. Understanding why it lost both is one of the most important questions in planetary science."),
    ('nova', "If you could drive a car at motorway speed straight up, you'd reach space in under an hour. The challenge is not the altitude — it's the velocity needed to stay there."),
    ('nova', "The Hubble Deep Field image was taken by pointing the telescope at a 'blank' patch of sky for 10 days. It revealed nearly 3,000 galaxies, each containing billions of stars."),
    ('nova', "Europa, one of Jupiter's moons, has a subsurface ocean that contains more liquid water than all of Earth's oceans combined. It is one of our best candidates for extraterrestrial life."),
    ('nova', "A day on Venus is longer than a year on Venus. It rotates so slowly that the sun rises in the west and sets in the east — and it takes 243 Earth days to complete one rotation."),
    ('nova', "The Cosmic Microwave Background radiation is the afterglow of the Big Bang, 380,000 years after it occurred. When you see static on an old TV, a tiny fraction of that noise is from the dawn of the universe."),
]

# (follower, following)
FOLLOWS = [
    ('alice', 'bob'), ('alice', 'charlie'), ('alice', 'diana'), ('alice', 'nova'),
    ('bob', 'alice'), ('bob', 'eve'), ('bob', 'frank'), ('bob', 'nova'),
    ('charlie', 'alice'), ('charlie', 'diana'), ('charlie', 'eve'), ('charlie', 'nova'),
    ('diana', 'alice'), ('diana', 'charlie'), ('diana', 'frank'), ('diana', 'nova'),
    ('eve', 'alice'), ('eve', 'bob'), ('eve', 'diana'), ('eve', 'nova'),
    ('frank', 'charlie'), ('frank', 'eve'), ('frank', 'bob'), ('frank', 'nova'),
    ('nova', 'alice'), ('nova', 'diana'), ('nova', 'eve'),
]

# (liker, post_author, post_index_for_that_author)  — 0-based index within author's posts
LIKES = [
    ('bob', 'alice', 0), ('charlie', 'alice', 1), ('diana', 'alice', 3),
    ('alice', 'bob', 0), ('eve', 'bob', 1), ('frank', 'bob', 3),
    ('alice', 'charlie', 0), ('diana', 'charlie', 1), ('eve', 'charlie', 3),
    ('alice', 'diana', 1), ('charlie', 'diana', 2), ('bob', 'diana', 3),
    ('alice', 'eve', 0), ('bob', 'eve', 2), ('diana', 'eve', 3),
    ('charlie', 'frank', 0), ('eve', 'frank', 2), ('alice', 'frank', 3),
    # nova's posts
    ('alice', 'nova', 0), ('bob', 'nova', 0), ('charlie', 'nova', 0),
    ('diana', 'nova', 1), ('eve', 'nova', 1), ('frank', 'nova', 1),
    ('alice', 'nova', 2), ('diana', 'nova', 2), ('charlie', 'nova', 3),
    ('bob', 'nova', 4), ('eve', 'nova', 4), ('frank', 'nova', 5),
    ('alice', 'nova', 6), ('diana', 'nova', 7), ('eve', 'nova', 8),
    ('charlie', 'nova', 9),
]

COMMENTS = [
    ('bob', 'alice', 0, "BFS on a to-do list is the most relatable thing I've read today."),
    ('diana', 'alice', 1, "Agreed! A good hash table makes me irrationally happy."),
    ('eve', 'charlie', 0, "QuickSort as jazz is chef's kiss. Stealing this analogy."),
    ('alice', 'diana', 1, "Congrats on the paper! Can't wait to read it."),
    ('charlie', 'eve', 0, "1000 PRs! You're a legend, Eve."),
    ('frank', 'charlie', 1, "I did the same thing last week. Heap properties are lowkey beautiful."),
    # comments on nova's posts
    ('alice', 'nova', 0, "The JWST images are absolutely breathtaking. Hard to process the scale of it all."),
    ('diana', 'nova', 0, "I used JWST data in a paper last year. The photometric precision is extraordinary."),
    ('charlie', 'nova', 2, "A billion tonnes per teaspoon. I need a moment to process that."),
    ('bob', 'nova', 3, "Voyager 1 is still going strong after nearly 50 years — incredible engineering."),
    ('eve', 'nova', 6, "The Hubble Deep Field is one of the most humbling images ever taken."),
    ('frank', 'nova', 9, "So when I hear static on an old radio I'm technically detecting ancient cosmic radiation? Mind blown."),
]


class Command(BaseCommand):
    help = 'Seed the database with example users, follows, posts, likes, and comments.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('Seeding Movo database...'))

        # ---------- Users ----------
        user_objs: dict[str, User] = {}
        for data in USERS:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'bio': data['bio'],
                    'website': data['website'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'password': make_password('password123'),
                },
            )
            user_objs[data['username']] = user
            status = 'created' if created else 'already exists'
            self.stdout.write(f"  User @{user.username} — {status}")

        # ---------- Posts ----------
        # Group posts by author username for index lookups
        author_posts: dict[str, list] = {u: [] for u in user_objs}
        for username, content in POSTS:
            user = user_objs[username]
            post, created = Post.objects.get_or_create(
                author=user,
                content=content,
            )
            author_posts[username].append(post)
            if created:
                self.stdout.write(f"  Post by @{username}: {content[:50]}...")

        # ---------- Follows ----------
        for follower_name, following_name in FOLLOWS:
            Follow.objects.get_or_create(
                follower=user_objs[follower_name],
                following=user_objs[following_name],
            )
        self.stdout.write(f"  {len(FOLLOWS)} follow relationships seeded.")

        # ---------- Likes ----------
        for liker_name, author_name, post_idx in LIKES:
            posts_list = author_posts.get(author_name, [])
            if post_idx < len(posts_list):
                Like.objects.get_or_create(
                    user=user_objs[liker_name],
                    post=posts_list[post_idx],
                )
        self.stdout.write(f"  {len(LIKES)} likes seeded.")

        # ---------- Comments ----------
        for commenter_name, author_name, post_idx, text in COMMENTS:
            posts_list = author_posts.get(author_name, [])
            if post_idx < len(posts_list):
                Comment.objects.get_or_create(
                    author=user_objs[commenter_name],
                    post=posts_list[post_idx],
                    content=text,
                )
        self.stdout.write(f"  {len(COMMENTS)} comments seeded.")

        self.stdout.write(self.style.SUCCESS('\nSeeding complete! Login with any username and password: password123'))
