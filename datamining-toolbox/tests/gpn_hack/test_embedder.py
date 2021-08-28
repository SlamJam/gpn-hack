from src.gpn_hack import embedder


def test_sema_embedder():
    model = embedder.load_ft_model('./ft_native_300_ru_wiki_lenta_lemmatize.bin')
    s = 'мама мыла раму'.split()
    res = embedder.sema_embedder(s, model)
    assert len(res) == 1200

