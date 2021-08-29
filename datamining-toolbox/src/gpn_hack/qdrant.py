import requests
from typing import Union, List, Dict
from random import random

# import embedder
Vector = List[float]


class QIndexer:

    def __init__(self, url, vector_size=1200):
        self.url = url
        self.vector_size = vector_size

    def create_collection(self, name):
        payload = {
            "create_collection": {
                "name": name,
                "vector_size": self.vector_size,
                "distance": "Cosine"
            }
        }

        r = requests.post(self.url + '/collections', json=payload)
        r.raise_for_status()

    def drop_collection(self, name):
        payload = {
            "delete_collection": name
        }

        r = requests.post(self.url + '/collections', json=payload)
        # r.raise_for_status()

    def embed(self, text: str) -> Vector:
        return [random() for x in range(1200)]

    def form_batch(self, docs_list: List[Dict], batch_size: int) -> List[Dict]:
        for i in range(0, len(docs_list) - 1, batch_size):
            yield docs_list[i: i + batch_size]

    # def form_point(self, doc: Dict) -> Dict:
    #     return {
    #         "id": doc["id"],
    #         "vector": self.embed(document["description"])
    #     return result

    def bulk_load(self, collection, points: List[Dict]):
        url = self.url + "/collections/" + collection

        payload = {"upsert_points": {"points": points}}
        r = requests.post(url, json=payload)
        r.raise_for_status()





# indexer = QIndexer()

# print(indexer.bulk_load(1, "localhost:6333", "companies", data))

# vect = [random() for i in range(1200)]
# qur = {
#     "filter": {"must": [{"key": "industries", "match": {"keyword": "res"}}]},
#     "vector": vect,
#     "top": 10,
# }
# print(
#     requests.post(
#         "http://localhost:6333/collections/companies/points/search", json=qur
#     ).json()
# )
