"""PostgreSQL-backed catalog API tests."""

from uuid import uuid4

from httpx import AsyncClient


async def create_item(
    client: AsyncClient,
    *,
    title: str = "The Left Hand of Darkness",
    author: str = "Ursula K. Le Guin",
    item_type: str = "book",
    status: str = "available",
):
    """Create a representative catalog item through the API."""
    return await client.post(
        "/api/python/catalog",
        json={
            "title": title,
            "author": author,
            "type": item_type,
            "status": status,
            "isbn": "9780441478125",
        },
    )


async def test_create_retrieve_list_update_and_delete(client: AsyncClient) -> None:
    """Exercise the catalog resource lifecycle."""
    created = await create_item(client)
    assert created.status_code == 201
    item = created.json()
    assert item["catalog_id"]

    retrieved = await client.get(f"/api/python/catalog/{item['id']}")
    assert retrieved.status_code == 200
    assert retrieved.json()["title"] == "The Left Hand of Darkness"

    listed = await client.get("/api/python/catalog")
    assert listed.status_code == 200
    assert [entry["id"] for entry in listed.json()] == [item["id"]]

    updated = await client.put(
        f"/api/python/catalog/{item['id']}",
        json={"title": "The Dispossessed", "status": "reserved"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "The Dispossessed"
    assert updated.json()["status"] == "reserved"

    deleted = await client.delete(f"/api/python/catalog/{item['id']}")
    assert deleted.status_code == 204
    assert (await client.get(f"/api/python/catalog/{item['id']}")).status_code == 404


async def test_search_and_filters(client: AsyncClient) -> None:
    """Search broad fields and filter by catalog type and status."""
    await create_item(client)
    await create_item(
        client,
        title="Arrival",
        author="Denis Villeneuve",
        item_type="dvd",
        status="borrowed",
    )

    by_author = await client.get(
        "/api/python/catalog",
        params={"search": "le guin"},
    )
    by_title = await client.get(
        "/api/python/catalog",
        params={"search": "Arrival"},
    )
    filtered = await client.get(
        "/api/python/catalog",
        params={"type": "dvd", "status": "borrowed"},
    )

    assert [item["title"] for item in by_author.json()] == ["The Left Hand of Darkness"]
    assert [item["title"] for item in by_title.json()] == ["Arrival"]
    assert [item["title"] for item in filtered.json()] == ["Arrival"]


async def test_generated_catalog_ids_are_unique(client: AsyncClient) -> None:
    """Reserve a different generated catalog ID for each item."""
    first = await create_item(client)
    second = await create_item(client, title="A Wizard of Earthsea")

    assert first.status_code == second.status_code == 201
    assert first.json()["catalog_id"] != second.json()["catalog_id"]


async def test_malformed_and_missing_identifiers(client: AsyncClient) -> None:
    """Distinguish malformed identifiers from absent valid UUIDs."""
    malformed = await client.get("/api/python/catalog/not-a-uuid")
    missing = await client.get(f"/api/python/catalog/{uuid4()}")
    missing_update = await client.put(
        f"/api/python/catalog/{uuid4()}",
        json={"title": "Missing"},
    )
    missing_delete = await client.delete(f"/api/python/catalog/{uuid4()}")

    assert malformed.status_code == 400
    assert malformed.json()["detail"] == "Invalid item ID format"
    assert missing.status_code == 404
    assert missing_update.status_code == 404
    assert missing_delete.status_code == 404
