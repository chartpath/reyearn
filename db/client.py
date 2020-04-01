import databases

db = databases.Database(
    "postgresql://localhost/reyearn_dev", ssl=False, min_size=5, max_size=20
)
