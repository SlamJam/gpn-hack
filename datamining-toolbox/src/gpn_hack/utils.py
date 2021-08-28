import json

import jsonlines


def save_pretty_json(data, fileobj):
    json.dump(data, fileobj, indent=2, sort_keys=True, ensure_ascii=False)


def save_jsonl(data, fileobj):
    with jsonlines.Writer(fileobj) as writer:
        writer.write_all(data)


def iter_over_jsonl(fileobj):
    with jsonlines.Reader(fileobj) as reader:
        yield from reader
