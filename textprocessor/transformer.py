from textprocessor.accentremover import AccentRemover
from textprocessor.expander import ContractionExpander
from textprocessor.lematizer import Lemmatizer
from textprocessor.linkremover import LinkRemover
from textprocessor.normalizer import Normalizer
from textprocessor.pipeline import Pipeline
from textprocessor.spellingfixer import SpellingFixer
from textprocessor.stemmer import Stemmer
from textprocessor.stopremover import StopwordRemover
from textprocessor.tokenizer import Tokenizer
from textprocessor.unicodecleaner import UnicodeCleaner
from textprocessor.validator import Validator
from textprocessor.whitespacecleaner import WhitespaceCleaner
from textprocessor.wordreplacer import WordReplacer


class DataTransformer:

    def __init__(self):
        self.pipeline = Pipeline([
            LinkRemover(),
            #AccentRemover(),
            UnicodeCleaner(),
            WhitespaceCleaner(),
            ContractionExpander(),
            Tokenizer(),
            #SpellingFixer(),
            Normalizer(),
            StopwordRemover(),
            WordReplacer(),
            #Lemmatizer(),
            Stemmer(),
            Validator()
        ])

    def __call__(self, data):
        return self.pipeline.transform(data)
