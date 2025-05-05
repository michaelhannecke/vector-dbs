# Repository Structure

```
vector-db-comparison/
├── LICENSE                    # MIT License
├── README.md                  # Main documentation
├── STRUCTURE.md               # This file
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore file
│
├── examples/                  # Example code for each vector database
│   ├── milvus_example.py      # Milvus example
│   ├── qdrant_example.py      # Qdrant example
│   ├── weaviate_example.py    # Weaviate example
│   ├── chroma_example.py      # Chroma example
│   ├── faiss_example.py       # FAISS example
│   └── vector_db_benchmark.py # Benchmark script for all databases
│
├── docker/                    # Docker configurations for each database
│   ├── milvus/                # Milvus Docker setup
│   │   └── docker-compose.yml
│   ├── qdrant/                # Qdrant Docker setup
│   │   └── docker-compose.yml
│   ├── weaviate/              # Weaviate Docker setup
│   │   └── docker-compose.yml
│   ├── chroma/                # Chroma Docker setup
│   │   └── docker-compose.yml
│   └── README.md              # Docker setup instructions
│
└── docs/                      # Additional documentation
    ├── milvus.md              # Milvus deep dive
    ├── qdrant.md              # Qdrant deep dive
    ├── weaviate.md            # Weaviate deep dive
    ├── chroma.md              # Chroma deep dive
    ├── faiss.md               # FAISS deep dive
    └── benchmarks.md          # Benchmarking methodology and results
```

## Directory Contents

### `/examples`

Contains executable Python examples for each vector database. These are the primary code samples that demonstrate how to use each database with similar patterns for comparison.

### `/docker`

Contains Docker Compose files to easily spin up each vector database for testing. This allows for consistent environments for benchmarking and experimentation.

### `/docs`

Contains detailed documentation about each vector database, including architecture details, unique features, and performance characteristics.