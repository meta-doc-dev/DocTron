from doctron_app.models import Collection, ShareCollection


def is_collection_accessible(username, collection_id, name_space):
    collection = Collection.objects.get(collection_id=collection_id)

    user_role = ShareCollection.objects.get(
        collection_id=collection_id,
        username=username,
        name_space=name_space
    )

    if collection.modality == "Collaborative open" or user_role.admin or user_role.reviewer:
        return True

    return False