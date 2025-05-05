"""
Weaviate Vector Database Example

This script demonstrates basic operations with Weaviate vector database:
- Connection setup
- Schema creation
- Data object creation with vectors
- Vector search using GraphQL
- Schema deletion

Requirements:
    pip install weaviate-client
"""

import random
import json
import weaviate
from weaviate.auth import AuthClientPassword

# Configuration
DIMENSION = 128  # Vector dimension
CLASS_NAME = "Article"
BATCH_SIZE = 100


def connect_to_weaviate():
    """Connect to Weaviate server"""
    print("Connecting to Weaviate...")

    # For local server without authentication
    client = weaviate.Client("http://localhost:8080")

    # If using authentication (uncomment and modify as needed)
    # client = weaviate.Client(
    #     url="http://localhost:8080",
    #     auth_client_secret=AuthClientPassword(
    #         username="admin",
    #         password="password"
    #     )
    # )

    print("Successfully connected to Weaviate!")
    return client


def create_schema(client):
    """Create a schema in Weaviate"""
    print(f"Checking if class '{CLASS_NAME}' exists...")

    # Check if class exists and delete it
    try:
        client.schema.get(CLASS_NAME)
        print(f"Class '{CLASS_NAME}' exists, deleting it...")
        client.schema.delete_class(CLASS_NAME)
        print(f"Class '{CLASS_NAME}' deleted.")
    except Exception:
        print(f"Class '{CLASS_NAME}' does not exist yet.")

    # Define class schema
    class_obj = {
        "class": CLASS_NAME,
        "description": "Example articles for vector search",
        "vectorizer": "none",  # We'll provide our own vectors
        "properties": [
            {
                "name": "title",
                "dataType": ["text"],
                "description": "Title of the article",
            },
            {
                "name": "content",
                "dataType": ["text"],
                "description": "Content of the article",
            },
            {
                "name": "category",
                "dataType": ["text"],
                "description": "Category of the article",
            },
            {
                "name": "rating",
                "dataType": ["number"],
                "description": "Rating of the article (1-5)",
            },
            {
                "name": "tags",
                "dataType": ["text[]"],
                "description": "Tags associated with the article",
            },
        ],
    }

    # Create the class
    client.schema.create_class(class_obj)
    print(f"Class '{CLASS_NAME}' created successfully!")


def generate_random_vector():
    """Generate a random vector"""
    return [random.random() for _ in range(DIMENSION)]


def insert_data_objects(client, num_objects=1000):
    """Insert data objects with vectors into Weaviate"""
    print(f"Generating {num_objects} random articles with vectors...")

    # Categories and tags for random selection
    categories = ["Technology", "Business", "Science", "Health", "Entertainment"]
    all_tags = [
        "AI",
        "Data",
        "Cloud",
        "Security",
        "Mobile",
        "Web",
        "ML",
        "Python",
        "Research",
        "Innovation",
        "Startup",
        "Enterprise",
        "Future",
        "Analysis",
    ]

    # Configure batch process
    client.batch.configure(batch_size=BATCH_SIZE)

    with client.batch as batch:
        for i in range(num_objects):
            # Create article data
            properties = {
                "title": f"Article {i + 1}: An Exploration of Topic {i % 20 + 1}",
                "content": f"This is the content of article {i + 1}. It contains information about topic {i % 20 + 1}.",
                "category": random.choice(categories),
                "rating": random.randint(1, 5),
                "tags": random.sample(all_tags, k=random.randint(1, 4)),
            }

            # Generate a random vector
            vector = generate_random_vector()

            # Add data object with vector
            batch.add_data_object(
                data_object=properties, class_name=CLASS_NAME, vector=vector
            )

            # Print progress
            if (i + 1) % BATCH_SIZE == 0 or i + 1 == num_objects:
                print(f"Added {i + 1}/{num_objects} articles")

    print(f"Inserted {num_objects} articles into Weaviate")


def vector_search(client, query_vector, class_fields=None, limit=5):
    """Search for similar vectors using Weaviate's GraphQL API"""
    print(f"Searching for top {limit} similar articles...")

    if class_fields is None:
        class_fields = ["title", "category", "rating"]

    result = (
        client.query.get(CLASS_NAME, class_fields)
        .with_near_vector({"vector": query_vector})
        .with_limit(limit)
        .do()
    )

    return result


def filter_search(client, query_vector, category, class_fields=None, limit=5):
    """Search for similar vectors with category filter"""
    print(f"Searching for top {limit} similar articles in category '{category}'...")

    if class_fields is None:
        class_fields = ["title", "category", "rating"]

    result = (
        client.query.get(CLASS_NAME, class_fields)
        .with_near_vector({"vector": query_vector})
        .with_where({"path": ["category"], "operator": "Equal", "valueText": category})
        .with_limit(limit)
        .do()
    )

    return result


def concept_search(client, concept, class_fields=None, limit=5):
    """Search using text concepts (if using text2vec module)"""
    print(f"Searching for articles related to concept '{concept}'...")

    if class_fields is None:
        class_fields = ["title", "category", "rating"]

    # Note: This requires a text vectorizer module to be configured
    result = (
        client.query.get(CLASS_NAME, class_fields)
        .with_near_text({"concepts": [concept]})
        .with_limit(limit)
        .do()
    )

    return result


def print_search_results(result, search_type="vector"):
    """Print search results in a readable format"""
    try:
        items = result["data"]["Get"][CLASS_NAME]
        print(f"\nSearch results ({search_type}):")
        for i, item in enumerate(items):
            print(f"  Result {i + 1}:")
            print(f"    Title: {item['title']}")
            print(f"    Category: {item['category']}")
            print(f"    Rating: {item['rating']}")
            print()
    except (KeyError, TypeError) as e:
        print(f"Error parsing results: {e}")
        print(f"Raw result: {json.dumps(result, indent=2)}")


def main():
    """Main function to demonstrate Weaviate operations"""
    try:
        # Connect to Weaviate
        client = connect_to_weaviate()

        # Create schema
        create_schema(client)

        # Insert data objects
        insert_data_objects(client, num_objects=500)

        # Generate a random query vector
        query_vector = generate_random_vector()

        # Perform vector search
        vector_result = vector_search(client, query_vector)
        print_search_results(vector_result, "vector")

        # Perform filtered search
        filtered_result = filter_search(client, query_vector, "Technology")
        print_search_results(filtered_result, "filtered by category 'Technology'")

        # Note: Concept search requires a text vectorizer module
        # concept_result = concept_search(client, "artificial intelligence")
        # print_search_results(concept_result, "concept 'artificial intelligence'")

        # Optionally delete the schema
        if input("\nDelete the schema? (y/n): ").lower() == "y":
            client.schema.delete_class(CLASS_NAME)
            print(f"Class '{CLASS_NAME}' deleted.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
