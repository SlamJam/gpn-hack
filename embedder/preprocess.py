import functools
import re
import string

import nltk
import pymorphy2
from nltk.corpus import stopwords

nltk.download("stopwords")


class Preprocess:
    def __init__(self):
        self.stopword = set(stopwords.words("russian"))
        self.morph = pymorphy2.MorphAnalyzer()

    def cleanhtml(self, raw_html):
        cleanr = re.compile("<.*?>")
        cleantext = re.sub(cleanr, "", raw_html)
        return cleantext

    def lowercase(self, text):
        return text.lower()

    def tokenize(self, text):
        text = self.cleanhtml(text)
        text = text.translate(str.maketrans("", "", string.punctuation))
        return [x for x in text.split(" ") if x != ""]

    def stopwords(self, token_list):
        return [x for x in token_list if x not in self.stopword]

    @functools.lru_cache
    def lematize(self, token):
        return self.morph.parse(token)[0].normal_form

    def process(self, text):
        result = self.lowercase(text)
        result = self.tokenize(result)
        result = self.stopwords(result)
        result = [self.lematize(x) for x in result]
        return result


##tests

# test = Preprocess()
# assert test.lowercase('Мама мыла в раму') == 'мама мыла в раму'
# assert test.tokenize('мама, мыла в раму') == ['мама', 'мыла','в' ,'раму']
# assert test.stopwords(['мама', 'мыла','в' ,'раму']) == ['мама', 'мыла' ,'раму']
# assert test.lematize('бежал') == 'бежать'
# assert test.process('Мама, мыла в раму') == ['мама', 'мыло', 'рама']
