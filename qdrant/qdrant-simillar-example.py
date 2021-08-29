import requests

"""
Example of rest-api queries for retrieving of simmilar companies
"""

# first we have one company id for similar companies
id_list = [5]

# then we need to get embeddings for this company, for that we can make request

qur = {"ids": id_list}


response = requests.post(
    "http://localhost:6333/collections/companies/points", json=qur
).json()

# in response we get storaged information of this id something like this
"""
{'result': [{'id': 5, 'payload': {'description': {'type': 'keyword', 'value': ['test']}, 'email': {'type': 'keyword', 'value': ['a@2']}, 'industries': {'type': 'keyword', 'value': ['124', 'res']}, 'name': {'type': 'keyword', 'value': ['tesasdft na12me']}, 'phone': {'type': 'keyword', 'value': ['12314']}}, 'vector': [0.004152137, 0.04047969, 0.010625124, 0.04005637, 0.039657533, 0.0044888076, 0.031646397, 0.0019378908, 0.0044049327, 0.021927595]}], 'status': 'ok', 'time': 1.733e-05}
"""

# we need to use .result[0].vector for vector search
vector = response["result"][0]["vector"]
# regular search query with top 3 simillar companies
query = {
    "vector": vector,
    "top": 3,
}
# post request
response = requests.post(
    "http://localhost:6333/collections/companies/points/search", json=query
).json()

"""
we get response like this. First result will be the company that we a looking with, so you can ignore it
{'result': [{'id': 5, 'score': 1.0000002}, {'id': 7, 'score': 0.7604941}, {'id': 6, 'score': 0.757956}], 'status': 'ok', 'time': 9.2889e-05}
"""

# from response we can extract companies id's
ids = [x['id'] for x in response['result']]

# after that, we want to extract information about companies
# to do that, we can request information by ids

qur = {"ids": ids}
response = requests.post(
    "http://localhost:6333/collections/companies/points", json=qur
).json()

# all information lay in response.result array in id and payload keys

companies = [{"id": x['id'], "name":x['payload']['name']['value'][0]}
             for x in response['result']]
print(companies)
