"""
Seed script for MiniBiblio test data.

Usage:
    uv run python -m api.scripts.seed_data          # Reset and seed (default)
    uv run python -m api.scripts.seed_data --reset  # Reset only (clear all data)
    uv run python -m api.scripts.seed_data --seed   # Seed only (add to existing)
"""

import asyncio
import argparse
import random
import uuid
from datetime import datetime, timezone

from sqlalchemy import delete, select
from api.db.database import async_session_factory
from api.db.models import (
    PatronDB,
    CatalogItemDB,
    LoanDB,
    PatronStatus,
    CatalogItemType,
    CatalogItemStatus,
)


# ============================================================================
# Sample Data
# ============================================================================

FIRST_NAMES = [
    # German names
    "Anna", "Max", "Sophie", "Felix", "Emma", "Leon", "Mia", "Paul", "Hannah", "Lukas",
    "Lena", "Jonas", "Laura", "Tim", "Julia", "David", "Sarah", "Niklas", "Lisa", "Jan",
    # English names
    "James", "Emily", "Michael", "Jessica", "William", "Ashley", "Daniel", "Amanda", "Matthew", "Stephanie",
    "Christopher", "Jennifer", "Andrew", "Elizabeth", "Joshua", "Megan", "Brandon", "Lauren", "Ryan", "Rachel",
    # International names
    "Sofia", "Mohammed", "Yuki", "Chen", "Maria", "Ali", "Aisha", "Carlos", "Fatima", "Raj",
]

LAST_NAMES = [
    # German surnames
    "Mueller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Hoffmann", "Schulz",
    "Koch", "Richter", "Klein", "Wolf", "Schroeder", "Neumann", "Schwarz", "Braun", "Zimmermann", "Hartmann",
    # English surnames
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Wilson", "Anderson", "Taylor",
    # International surnames
    "Garcia", "Martinez", "Chen", "Wang", "Patel", "Kim", "Nguyen", "Ali", "Singh", "Tanaka",
]

BOOK_TITLES = [
    # Classics
    ("Pride and Prejudice", "Jane Austen", "Fiction"),
    ("1984", "George Orwell", "Science Fiction"),
    ("To Kill a Mockingbird", "Harper Lee", "Fiction"),
    ("The Great Gatsby", "F. Scott Fitzgerald", "Fiction"),
    ("One Hundred Years of Solitude", "Gabriel Garcia Marquez", "Fiction"),
    ("The Catcher in the Rye", "J.D. Salinger", "Fiction"),
    ("Brave New World", "Aldous Huxley", "Science Fiction"),
    ("The Lord of the Rings", "J.R.R. Tolkien", "Fantasy"),
    ("Harry Potter and the Sorcerer's Stone", "J.K. Rowling", "Fantasy"),
    ("The Hobbit", "J.R.R. Tolkien", "Fantasy"),
    # Mystery/Thriller
    ("The Girl with the Dragon Tattoo", "Stieg Larsson", "Mystery"),
    ("Gone Girl", "Gillian Flynn", "Thriller"),
    ("The Da Vinci Code", "Dan Brown", "Thriller"),
    ("Murder on the Orient Express", "Agatha Christie", "Mystery"),
    ("The Silent Patient", "Alex Michaelides", "Thriller"),
    # Science Fiction
    ("Dune", "Frank Herbert", "Science Fiction"),
    ("Foundation", "Isaac Asimov", "Science Fiction"),
    ("Neuromancer", "William Gibson", "Science Fiction"),
    ("The Martian", "Andy Weir", "Science Fiction"),
    ("Project Hail Mary", "Andy Weir", "Science Fiction"),
    # Non-Fiction
    ("A Brief History of Time", "Stephen Hawking", "Science"),
    ("Sapiens", "Yuval Noah Harari", "History"),
    ("Thinking, Fast and Slow", "Daniel Kahneman", "Psychology"),
    ("The Selfish Gene", "Richard Dawkins", "Science"),
    ("Guns, Germs, and Steel", "Jared Diamond", "History"),
    # German Literature
    ("Die Verwandlung", "Franz Kafka", "Fiction"),
    ("Der Prozess", "Franz Kafka", "Fiction"),
    ("Faust", "Johann Wolfgang von Goethe", "Drama"),
    ("Die Blechtrommel", "Guenter Grass", "Fiction"),
    ("Der Vorleser", "Bernhard Schlink", "Fiction"),
    # Modern Fiction
    ("The Kite Runner", "Khaled Hosseini", "Fiction"),
    ("Life of Pi", "Yann Martel", "Fiction"),
    ("The Book Thief", "Markus Zusak", "Fiction"),
    ("A Man Called Ove", "Fredrik Backman", "Fiction"),
    ("Where the Crawdads Sing", "Delia Owens", "Fiction"),
    # Biography
    ("Steve Jobs", "Walter Isaacson", "Biography"),
    ("Becoming", "Michelle Obama", "Biography"),
    ("Einstein: His Life and Universe", "Walter Isaacson", "Biography"),
    ("The Diary of a Young Girl", "Anne Frank", "Biography"),
    ("Long Walk to Freedom", "Nelson Mandela", "Biography"),
    # More titles
    ("The Alchemist", "Paulo Coelho", "Fiction"),
    ("The Name of the Wind", "Patrick Rothfuss", "Fantasy"),
    ("Ender's Game", "Orson Scott Card", "Science Fiction"),
    ("The Hunger Games", "Suzanne Collins", "Science Fiction"),
    ("Twilight", "Stephenie Meyer", "Fantasy"),
    ("The Fault in Our Stars", "John Green", "Fiction"),
    ("Ready Player One", "Ernest Cline", "Science Fiction"),
    ("The Handmaid's Tale", "Margaret Atwood", "Science Fiction"),
    ("Cloud Atlas", "David Mitchell", "Fiction"),
    ("Norwegian Wood", "Haruki Murakami", "Fiction"),
]

DVD_TITLES = [
    ("The Shawshank Redemption", "Drama"),
    ("Inception", "Science Fiction"),
    ("The Dark Knight", "Action"),
    ("Pulp Fiction", "Drama"),
    ("Forrest Gump", "Drama"),
    ("The Matrix", "Science Fiction"),
    ("Interstellar", "Science Fiction"),
    ("The Godfather", "Drama"),
    ("Fight Club", "Drama"),
    ("Goodfellas", "Drama"),
    ("Schindler's List", "Drama"),
    ("The Lord of the Rings: Fellowship", "Fantasy"),
    ("Gladiator", "Action"),
    ("The Silence of the Lambs", "Thriller"),
    ("Saving Private Ryan", "War"),
]

CD_TITLES = [
    ("Abbey Road", "The Beatles"),
    ("Thriller", "Michael Jackson"),
    ("Back in Black", "AC/DC"),
    ("The Dark Side of the Moon", "Pink Floyd"),
    ("Rumours", "Fleetwood Mac"),
    ("Nevermind", "Nirvana"),
    ("21", "Adele"),
    ("1989", "Taylor Swift"),
    ("OK Computer", "Radiohead"),
    ("Kind of Blue", "Miles Davis"),
]

MAGAZINE_TITLES = [
    "National Geographic",
    "Scientific American",
    "The Economist",
    "Time Magazine",
    "Der Spiegel",
]

PUBLISHERS = [
    "Penguin Random House", "HarperCollins", "Simon & Schuster",
    "Macmillan", "Hachette", "Scholastic", "Wiley", "Oxford University Press",
    "Cambridge University Press", "Suhrkamp Verlag", "Fischer Verlag",
]


# ============================================================================
# Helper Functions
# ============================================================================

def generate_membership_id() -> str:
    """Generate a unique membership ID."""
    return f"LIB-{str(uuid.uuid4())[:8].upper()}"


def generate_catalog_id() -> str:
    """Generate a unique catalog ID."""
    return f"CAT-{str(uuid.uuid4())[:8].upper()}"


def generate_isbn() -> str:
    """Generate a realistic ISBN-13."""
    prefix = "978"
    group = str(random.randint(0, 9))
    publisher = str(random.randint(1000, 9999))
    title = str(random.randint(10000, 99999))
    return f"{prefix}-{group}-{publisher}-{title}-{random.randint(0, 9)}"


def generate_phone(german: bool = True) -> str:
    """Generate a phone number."""
    if german:
        return f"+49-{random.randint(100, 999)}-{random.randint(1000000, 9999999)}"
    return f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"


def generate_location() -> str:
    """Generate a shelf location."""
    row = random.choice(["A", "B", "C", "D"])
    num = random.randint(1, 10)
    return f"Shelf {row}{num}"


# ============================================================================
# Database Operations
# ============================================================================

async def reset_data(session) -> None:
    """Delete all data in correct order (respecting foreign keys)."""
    print("Resetting data...")

    # Delete loans first (references patrons and catalog items)
    result = await session.execute(delete(LoanDB))
    print(f"  Deleted {result.rowcount} loans")

    # Delete patrons
    result = await session.execute(delete(PatronDB))
    print(f"  Deleted {result.rowcount} patrons")

    # Delete catalog items
    result = await session.execute(delete(CatalogItemDB))
    print(f"  Deleted {result.rowcount} catalog items")

    await session.commit()
    print("Reset complete!")


async def seed_patrons(session, count: int = 50) -> None:
    """Create test patrons."""
    print(f"Seeding {count} patrons...")

    patrons = []
    used_emails = set()

    for i in range(count):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)

        # Generate unique email
        base_email = f"{first_name.lower()}.{last_name.lower()}@example.com"
        email = base_email
        counter = 1
        while email in used_emails:
            email = f"{first_name.lower()}.{last_name.lower()}{counter}@example.com"
            counter += 1
        used_emails.add(email)

        # Determine status (80% active, 15% inactive, 5% suspended)
        status_roll = random.random()
        if status_roll < 0.80:
            status = PatronStatus.active
        elif status_roll < 0.95:
            status = PatronStatus.inactive
        else:
            status = PatronStatus.suspended

        patron = PatronDB(
            membership_id=generate_membership_id(),
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=generate_phone(german=random.random() < 0.6),
            status=status,
        )
        patrons.append(patron)

    session.add_all(patrons)
    await session.flush()
    print(f"  Created {len(patrons)} patrons")


async def seed_catalog_items(session, count: int = 100) -> None:
    """Create test catalog items."""
    print(f"Seeding {count} catalog items...")

    items = []

    # Distribution: 70 books, 15 DVDs, 10 CDs, 5 magazines
    book_count = int(count * 0.70)
    dvd_count = int(count * 0.15)
    cd_count = int(count * 0.10)
    magazine_count = count - book_count - dvd_count - cd_count

    # Create books
    book_titles_shuffled = BOOK_TITLES.copy()
    random.shuffle(book_titles_shuffled)

    for i in range(book_count):
        title_data = book_titles_shuffled[i % len(book_titles_shuffled)]
        title, author, genre = title_data

        # Make title unique if reusing
        if i >= len(book_titles_shuffled):
            title = f"{title} (Edition {i // len(book_titles_shuffled) + 1})"

        # Status distribution (85% available, 10% borrowed, 5% other)
        status_roll = random.random()
        if status_roll < 0.85:
            status = CatalogItemStatus.available
        elif status_roll < 0.95:
            status = CatalogItemStatus.borrowed
        else:
            status = random.choice([CatalogItemStatus.reserved, CatalogItemStatus.damaged, CatalogItemStatus.lost])

        # Language (85% English, 10% German, 5% Spanish)
        lang_roll = random.random()
        if lang_roll < 0.85:
            language = "English"
        elif lang_roll < 0.95:
            language = "German"
        else:
            language = "Spanish"

        item = CatalogItemDB(
            catalog_id=generate_catalog_id(),
            type=CatalogItemType.book,
            title=title,
            author=author,
            isbn=generate_isbn(),
            publisher=random.choice(PUBLISHERS),
            year=random.randint(1950, 2024),
            genre=genre,
            language=language,
            location=generate_location(),
            status=status,
        )
        items.append(item)

    # Create DVDs
    dvd_titles_shuffled = DVD_TITLES.copy()
    random.shuffle(dvd_titles_shuffled)

    for i in range(dvd_count):
        title_data = dvd_titles_shuffled[i % len(dvd_titles_shuffled)]
        title, genre = title_data

        item = CatalogItemDB(
            catalog_id=generate_catalog_id(),
            type=CatalogItemType.dvd,
            title=title,
            genre=genre,
            year=random.randint(1990, 2024),
            language="English",
            location=generate_location(),
            status=CatalogItemStatus.available if random.random() < 0.85 else CatalogItemStatus.borrowed,
        )
        items.append(item)

    # Create CDs
    cd_titles_shuffled = CD_TITLES.copy()
    random.shuffle(cd_titles_shuffled)

    for i in range(cd_count):
        title_data = cd_titles_shuffled[i % len(cd_titles_shuffled)]
        title, artist = title_data

        item = CatalogItemDB(
            catalog_id=generate_catalog_id(),
            type=CatalogItemType.cd,
            title=title,
            author=artist,  # Using author field for artist
            year=random.randint(1960, 2024),
            genre="Music",
            location=generate_location(),
            status=CatalogItemStatus.available,
        )
        items.append(item)

    # Create Magazines
    for i in range(magazine_count):
        title = random.choice(MAGAZINE_TITLES)
        issue_num = random.randint(1, 52)
        year = random.randint(2020, 2024)

        item = CatalogItemDB(
            catalog_id=generate_catalog_id(),
            type=CatalogItemType.magazine,
            title=f"{title} - Issue {issue_num}/{year}",
            year=year,
            language="English" if title != "Der Spiegel" else "German",
            location=generate_location(),
            status=CatalogItemStatus.available,
        )
        items.append(item)

    session.add_all(items)
    await session.flush()
    print(f"  Created {len(items)} catalog items ({book_count} books, {dvd_count} DVDs, {cd_count} CDs, {magazine_count} magazines)")


# ============================================================================
# Main
# ============================================================================

async def main(reset: bool = True, seed: bool = True) -> None:
    """Main entry point."""
    async with async_session_factory() as session:
        if reset:
            await reset_data(session)

        if seed:
            await seed_patrons(session, 50)
            await seed_catalog_items(session, 100)
            await session.commit()
            print("Seeding complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed MiniBiblio test data")
    parser.add_argument("--reset", action="store_true", help="Reset data only (clear all)")
    parser.add_argument("--seed", action="store_true", help="Seed data only (add to existing)")
    args = parser.parse_args()

    # Default: both reset and seed
    if not args.reset and not args.seed:
        reset = True
        seed = True
    else:
        reset = args.reset
        seed = args.seed

    asyncio.run(main(reset=reset, seed=seed))
