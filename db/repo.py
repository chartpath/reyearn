async def create_one_observation(db, text):
    print(db)


async def create_annotations(db, class_id, observation_id):
    print(db, class_id, observation_id)
    return {"msg": "created"}


async def fetch_annotations(db):
    print(db)
    return [{"class_id": 0, "observation_id": 0}]
