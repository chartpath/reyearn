import databases

# There are multiple clients created by the app: server, importer and trainer.
# Multiply min and max connections by 3 when planning runtime infra.
# Standalone DAG runs will add their own clients as well.
# To inject a single client everywhere, add it to the app.state object.
db = databases.Database(
    "postgresql://localhost/reyearn_dev", ssl=False, min_size=5, max_size=20
)
