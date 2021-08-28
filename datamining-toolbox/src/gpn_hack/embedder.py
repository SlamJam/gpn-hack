import numpy as np
import fasttext

def load_ft_model(fpath):
    return fasttext.load_model(fpath)

def agg_sent_vectors(vectors, agg_funcs, axis=0):
    vects = (agg_func(vectors, axis=axis) for agg_func in agg_funcs)
    return list(np.hstack([*vects]))

def combine_processors(tokens, processors):
    vectors = (processor(tokens) for processor in processors)
    return np.hstack([*vectors])

def sema_embedder(tokens, model, weights=None, aggs=(np.mean, np.max, np.min, np.std)):
    if not hasattr(model, 'get_word_vector'):
        raise NotImplementedError
    if weights is None:
        weights = np.ones_like(tokens).astype('float')
    vects = [model.get_word_vector(token) * weight for token, weight in zip(tokens, weights)]
    return agg_sent_vectors(vects, aggs)