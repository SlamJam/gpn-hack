curl -X POST 'http://localhost:6333/collections' \
    -H 'Content-Type: application/json' \
    --data-raw '{
        "create_collection": {
            "name": "companies",
            "vector_size": 1200,
            "distance": "Cosine"
        }
    }'
