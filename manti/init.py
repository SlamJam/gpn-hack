from __future__ import print_function

import time
import manticoresearch
import json
from manticoresearch.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://127.0.0.1:9308
# See configuration.py for a list of all supported configuration parameters.
configuration = manticoresearch.Configuration(
    host = "http://127.0.0.1:9308"
)



# Enter a context with an instance of the API client
with manticoresearch.ApiClient(configuration) as api_client:
    ##creating table
    api_instance = manticoresearch.UtilsApi(api_client)
    res = api_instance.sql('mode=raw&query=CREATE TABLE if not exists companies(\
        name text stored indexed, email text stored indexed, phone text, description text stored indexed \
        , name_morph text indexed, description_morph text indexed)  \
         min_prefix_len = \'3\' morphology = \'stem_ru\' stopwords = \'ru\'  morphology_skip_fields = \'name,phone,email,description\'')
    print(res)
    #res = api_instance.sql('mode=raw&query=SHOW TABLES')
    #print(res)
    

    ## bulk index method
    api_instance = manticoresearch.IndexApi(api_client)
    docs = [ \
    {"insert": {"index" : "companies", "id" : 1, "doc" : {"name" : "Сбермаркет", "email" : "kself@faesf.ru", "phone" : "213123", "description": "test", "name_morph":"сбермаркет молоко"}}}, \
    {"insert": {"index" : "companies", "id" : 2, "doc" : {"name" : "Газпром", "email" : "kself@test.ru", "phone" : "213123", "description": "another one bytes the dust"}}}
]
    #res = api_instance.bulk('\n'.join(map(json.dumps,docs)))
    #print(res)

    api_instance = manticoresearch.SearchApi(api_client)
    # field match
    res = api_instance.search({"index":"companies","query":{"match":{"name_morph":'молоко'}}})
    print(res)