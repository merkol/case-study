import requests
from datetime import datetime, timezone

FIRESTORE_EMULATOR_URL = "http://localhost:8080"
PROJECT_ID = "case-study-feraset"


def to_firestore_value(value):
    if isinstance(value, str):
        return {"stringValue": value}
    elif isinstance(value, bool):  # Check bool before int since bool is subclass of int
        return {"booleanValue": value}
    elif isinstance(value, int):
        return {"integerValue": str(value)}  # MUST be string!
    elif isinstance(value, float):
        return {"doubleValue": value}
    elif isinstance(value, datetime):
        return {
            "timestampValue": value.astimezone(timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z")
        }
    elif value is None:
        return {"nullValue": None}
    elif isinstance(value, dict):
        return {
            "mapValue": {"fields": {k: to_firestore_value(v) for k, v in value.items()}}
        }
    elif isinstance(value, list):
        return {"arrayValue": {"values": [to_firestore_value(v) for v in value]}}
    else:
        raise TypeError(f"Unsupported type: {type(value)}")


def create_document(collection, doc_id, data):
    # Use POST with documentId parameter for consistent behavior
    url = f"{FIRESTORE_EMULATOR_URL}/v1/projects/{PROJECT_ID}/databases/(default)/documents/{collection}"

    fields = {k: to_firestore_value(v) for k, v in data.items()}
    payload = {"fields": fields}

    # Add documentId to URL parameters if specified
    params = {}
    if doc_id:
        params["documentId"] = doc_id

        headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers, params=params)

    if response.status_code in [200, 201]:
        print(f"  ✓ Created {collection}/{doc_id}")
    else:
        print(f"  ✗ Failed to create {collection}/{doc_id}: {response.text}")


def setup_test_data():
    print("Setting up Firebase Emulator test data...")
    print("=" * 50)

    now = datetime.now(timezone.utc)

    # Users
    print("\nCreating test users...")
    users = [
        (
            "testuser1",
            {
                "userId": "testuser1",
                "email": "testuser1@example.com",
                "credits": 100,
                "createdAt": now,
                "updatedAt": now,
            },
        ),
        (
            "testuser2",
            {
                "userId": "testuser2",
                "email": "testuser2@example.com",
                "credits": 50,
                "createdAt": now,
                "updatedAt": now,
            },
        ),
        (
            "testuser3",
            {
                "userId": "testuser3",
                "email": "testuser3@example.com",
                "credits": 10,
                "createdAt": now,
                "updatedAt": now,
            },
        ),
    ]

    for uid, data in users:
        create_document("users", uid, data)

    # Colors
    print("\nCreating colors...")
    colors = ["vibrant", "monochrome", "pastel", "neon", "vintage"]
    for color in colors:
        create_document(
            "colors", color, {"name": color, "active": True, "createdAt": now}
        )

    # Styles
    print("\nCreating styles...")
    styles = ["realistic", "anime", "oil painting", "sketch", "cyberpunk", "watercolor"]
    for style in styles:
        create_document(
            "styles", style, {"name": style, "active": True, "createdAt": now}
        )

    # Sizes
    print("\nCreating sizes...")
    sizes = [
        ("512x512", {"name": "512x512", "credits": 1, "width": 512, "height": 512}),
        (
            "1024x1024",
            {"name": "1024x1024", "credits": 3, "width": 1024, "height": 1024},
        ),
        (
            "1024x1792",
            {"name": "1024x1792", "credits": 4, "width": 1024, "height": 1792},
        ),
    ]

    for size_id, data in sizes:
        data.update({"active": True, "createdAt": now})
        create_document("sizes", size_id, data)

    print("\n✅ Test data setup complete!")
    print("You can view the data in the Emulator UI at: http://localhost:4000")


if __name__ == "__main__":
    try:
        requests.get(f"{FIRESTORE_EMULATOR_URL}/")
        print("✓ Firestore emulator is running")
        setup_test_data()
    except requests.exceptions.ConnectionError:
        print("✗ Error: Firestore emulator is not running!")
        print("  Please run 'firebase emulators:start'")
        exit(1)
