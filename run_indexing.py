from indexer.indexer import Indexer


if __name__ == "__main__":
    with open('./data/hydrated_tweets.csv', 'rb') as file:
        idxer = Indexer(file)
        idxer.start()
