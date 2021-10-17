from textprocessor.transformer import DataTransformer
from indexer.delayedinterrupt import DelayedKeyboardInterrupt
from jsonpickle import encode, decode
from datetime import datetime
from typing import BinaryIO
from json import dump, load
from tqdm import tqdm
import time


class Indexer:
    __dec = {'#': 'hashtag', '@': 'tag'}

    __counts = {2: {}, 5: {}, 8: {}, 15: {}, 25: {}, 37: {}, 50: {}, 65: {}, 85: {},
                100: {}, 200: {}, 300: {}, 400: {}, 500: {}, 1000: {}, 5000: {}, 10000: {},
                20000: {}, 50000: {}, 100000: {}, 200000: {}, 500000: {}, 1000000: {},
                2000000: {}, 5000000: {}, 10000000: {}, 50000000: {}}

    def __init__(self, file: BinaryIO):
        if 'b' not in file.mode:
            raise RuntimeError('File must be opened in binary mode')

        self.tf = DataTransformer()
        self.checkpoint, self.idx_checkpoint = self.__load_checkpoint()
        self.last_check = self.checkpoint
        self.previous_idx = self.idx_checkpoint
        self.index_dict, self.frequency_dict, self.time_dict, self.file_line_index = self.__load_dicts()
        self.tweet_file = file
        self.tweet_file.seek(self.checkpoint)

    def __del__(self):  # We need a destructor here to close file and release large resources, and to save
        del self.index_dict
        del self.frequency_dict
        del self.time_dict

    def start(self):
        try:
            self.__indexing()
        except KeyboardInterrupt:
            print("Interrupted")
            self.__save_dicts()
            self.__save_checkpoint()
        except IndexError as e:
            self.file_line_index.pop()
            self.checkpoint = self.last_check
            self.idx_checkpoint = self.previous_idx
            self.__save_dicts()
            self.__save_checkpoint()
            raise e
        except BaseException as e:
            raise e

    def __indexing(self):
        for idx, tweet in tqdm(enumerate(self.tweet_file), initial=self.idx_checkpoint, total=176780):
            with DelayedKeyboardInterrupt():
                self.file_line_index.append(self.checkpoint)
                self.checkpoint = self.tweet_file.tell()
                tweet = tweet.decode('utf-8').strip().split('\t')
                tweet = {"user": tweet[0], "text": tweet[1], "favorites": int(tweet[2]),
                         "retweets": int(tweet[3]), "time": int(tweet[4])}

                self.__process_text(self.tf(tweet['text']), idx + self.idx_checkpoint)
                self.__process_user(tweet['user'], idx + self.idx_checkpoint)
                self.__process_favorites_retweets(tweet['favorites'], tweet['retweets'], idx + self.idx_checkpoint)
                self.__process_time(tweet['time'], idx + self.idx_checkpoint)
                self.last_check = self.checkpoint
                self.previous_idx += 1

        self.idx_checkpoint = self.previous_idx
        self.__save_dicts()
        self.__save_checkpoint()

    def __process_time(self, timestamp: int, idx: int):
        timed = datetime.date(datetime.fromtimestamp(timestamp))
        timed = int(time.mktime(timed.timetuple()))

        if timed in self.time_dict:
            self.time_dict[timed].add(idx)
        else:
            self.time_dict[timed] = {idx}

    def __process_favorites_retweets(self, favorites: int, retweets: int, idx: int):
        best_fav = None
        best_rt = None
        best_fav_done = False
        best_rt_done = False

        for key in list(self.__class__.__counts.keys())[::-1]:
            if favorites <= key and not best_fav_done:
                best_fav = key
            else:
                best_fav_done = True

            if retweets <= key and not best_rt_done:
                best_rt = key
            else:
                best_rt_done = True

        self.index_dict['favorites'][str(best_fav)].add(idx)
        self.index_dict['retweets'][str(best_rt)].add(idx)

    def __process_user(self, user: str, idx: int):
        if user in self.index_dict['user']:
            self.index_dict['user'][user].add(idx)
        else:
            self.index_dict['user'][user] = {idx}

    def __process_text(self, token_list: list, idx: int):
        for word in token_list:
            if "#" in word and word[0] != "#":
                new = word.split("#")
                word = new[0]
            if word[0] not in ('#', '@'):
                if word in self.frequency_dict:
                    self.frequency_dict[word] += 1
                    self.index_dict['text'][word][idx] = token_list.count(word)
                else:
                    self.frequency_dict[word] = 1
                    self.index_dict['text'][word] = {}
                    self.index_dict['text'][word][idx] = token_list.count(word)
            else:
                if word in self.index_dict[self.__class__.__dec[word[0]]]:
                    self.index_dict[self.__class__.__dec[word[0]]][word].add(idx)
                else:
                    self.index_dict[self.__class__.__dec[word[0]]][word] = {idx}

    def __save_dicts(self):
        with DelayedKeyboardInterrupt():
            with open('./resources/frequency.dat', 'w', encoding='utf-8') as freqfile, \
                    open('./resources/index.dat', 'w', encoding='utf-8') as indexfile, \
                    open('./resources/timeindex.dat', 'w', encoding='utf-8') as timeindexfile, \
                    open('./resources/fileindex.dat', 'w', encoding='utf-8') as fileindexfile:
                dump(encode(self.index_dict), indexfile, ensure_ascii=False, separators=(',', ':'))
                dump(encode(self.frequency_dict), freqfile, ensure_ascii=False, separators=(',', ':'))
                dump(encode(self.time_dict), timeindexfile, ensure_ascii=False, separators=(',', ':'))
                dump(encode(self.file_line_index), fileindexfile, ensure_ascii=False, separators=(',', ':'))

    @staticmethod
    def __load_dicts():
        with open('./resources/frequency.dat', 'r', encoding='utf-8') as freqfile, \
                open('./resources/index.dat', 'r', encoding='utf-8') as indexfile, \
                open('./resources/timeindex.dat', 'r', encoding='utf-8') as timeindexfile, \
                open('./resources/fileindex.dat', 'r', encoding='utf-8') as fileindexfile:
            return decode(load(indexfile)), decode(load(freqfile)), \
                   decode(load(timeindexfile)), decode(load(fileindexfile))

    @staticmethod
    def __load_checkpoint():
        with open('./resources/indexcheckpoint.dat', 'r') as file:
            return [int(x) for x in file.readline().strip().split(',')]

    def __save_checkpoint(self):
        with open('./resources/indexcheckpoint.dat', 'w') as file:
            file.write("{},{}".format(self.checkpoint, self.idx_checkpoint))
