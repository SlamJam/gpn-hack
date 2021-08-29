import requests
from typing import Union, List, Dict
from random import random

# import embedder
Vector = List[float]


class QIndexer:
    def init(self):
        pass

    def embed(self, text: str) -> Vector:
        return [random() for x in range(1200)]

    def form_batch(self, docs_list: List[Dict], batch_size: int) -> List[Dict]:
        for i in range(0, len(docs_list) - 1, batch_size):
            yield docs_list[i : i + batch_size]

    def form_point(self, document: Dict) -> Dict:
        result = {}
        result["id"] = document["id"]
        result["vector"] = self.embed(document["description"])
        result["payload"] = {
            "name": document["name"],
            "email": document["email"],
            "phone": document["phone"],
            "description": document["description"],
            "industries": document["industries"],
        }
        return result

    def bulk_load(self, batch_size, host, collection, docs_list: List[Dict]) -> str:
        batcher = self.form_batch(docs_list, batch_size)
        url = "http://" + host + "/collections/" + collection
        for batch in batcher:
            points = [self.form_point(document) for document in batch]
            batch_load = {"upsert_points": {"points": points}}
            test = requests.post(url, json=batch_load)
            print(test)
        return "Success"


data = [
    {
        "id": 5,
        "description": "test",
        "name": "tesasdft na12me",
        "email": "a@2",
        "phone": "12314",
        "industries": ["124", "res"],
    },
    {
        "id": 6,
        "description": "teasdfgasegasegst",
        "name": "test n12ame",
        "email": "a@2",
        "phone": "532188",
        "industries": ["124", "segaji"],
    },
    {
        "id": 7,
        "description": "teweasdfgqwegqwest",
        "name": "test n12ame",
        "email": "a@2",
        "phone": "1231244",
        "industries": ["124", "res"],
    },
    {
        "id": 8,
        "description": "teqwsadfasdfegqwegst",
        "name": "test n12ame",
        "email": "a@2",
        "phone": "5128125",
        "industries": ["124", "res"],
    },
]
indexer = QIndexer()

print(indexer.bulk_load(1, "localhost:6333", "companies", data))
vect = [random() for i in range(1200)]
qur = {
    "filter": {"must": [{"key": "industries", "match": {"keyword": "res"}}]},
    "vector": vect,
    "top": 3,
}
print(
    requests.post(
        "http://localhost:6333/collections/companies/points/search", json=qur
    ).json()
)
