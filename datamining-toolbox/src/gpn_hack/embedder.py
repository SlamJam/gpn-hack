import fasttext
import gensim
import numpy as np


def load_ft_model(fpath):
    return fasttext.load_model(fpath)


def load_gensim_model(fpath):
    return gensim.models.fasttext.FastTextKeyedVectors.load(fpath)


def agg_sent_vectors(vectors, agg_funcs, axis=0):
    vects = (agg_func(vectors, axis=axis) for agg_func in agg_funcs)
    return list(np.hstack([*vects]))


def combine_processors(tokens, processors):
    vectors = (processor(tokens) for processor in processors)
    return np.hstack([*vectors])


def sema_embedder(tokens, model, weights=None, aggs=(np.mean, np.max, np.min, np.std)):
    if weights is None:
        weights = np.ones_like(tokens).astype("float")
    if hasattr(model, "get_word_vector"):
        vects = [model.get_word_vector(token) * weight for token, weight in zip(tokens, weights)]
    else:
        vects = [model.wv[token] * weight for token, weight in zip(tokens, weights)]
    return agg_sent_vectors(vects, aggs)


# TODO: old
# def sema_embedder(tokens, model, weights=None, aggs=(np.mean, np.max, np.min, np.std)):
#     if not hasattr(model, 'get_word_vector'):
#         raise NotImplementedError
#     if weights is None:
#         weights = np.ones_like(tokens).astype('float')
#     vects = [model.get_word_vector(token) * weight for token, weight in zip(tokens, weights)]
#     return agg_sent_vectors(vects, aggs)


# fpath_model = './ft_model_small.bin'
# ft_model = load_gensim_model(fpath_model)

# text = 'мама мыла раму'
# vec = sema_embedder(text.split(), ft_model)
# print(vec[:4])
# # [-0.3421990686655045,
# # 0.0455693667246184,
# # 0.1381901032520303,
# # 0.2537064249437999]


# fasttext = "^0.9.2"
# gensim = "3.8.3"
# compress-fasttext = "^0.0.7"
