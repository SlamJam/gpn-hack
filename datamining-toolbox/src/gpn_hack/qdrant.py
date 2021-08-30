from typing import Dict, List

import requests


Vector = List[float]


class QIndexer:
    def __init__(self, url, vector_size=1200):
        self.url = url
        self.vector_size = vector_size

    def create_collection(self, name):
        payload = {"create_collection": {"name": name, "vector_size": self.vector_size, "distance": "Cosine"}}

        r = requests.post(self.url + "/collections", json=payload)
        r.raise_for_status()

    def drop_collection(self, name):
        payload = {"delete_collection": name}

        r = requests.post(self.url + "/collections", json=payload)
        # r.raise_for_status()

    def bulk_load(self, collection, points: List[Dict]):
        url = self.url + "/collections/" + collection

        payload = {"upsert_points": {"points": list(points)}}
        r = requests.post(url, json=payload)
        r.raise_for_status()

    def similar_topn(self, collection, vector: Vector, n):
        payload = {
            "vector": vector,
            "top": n,
        }

        url = self.url + f"/collections/{collection}/points/search"
        r = requests.post(url, json=payload)
        r.raise_for_status()

        data = r.json()
        return [d["id"] for d in data["result"]]
