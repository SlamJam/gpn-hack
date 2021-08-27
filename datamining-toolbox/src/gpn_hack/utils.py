import json


def save_pretty_json(data, fileobj):
    json.dump(data, fileobj, indent=2, sort_keys=True, ensure_ascii=False)
