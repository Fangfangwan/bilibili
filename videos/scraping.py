import pandas as pd
import gensim
import sklearn
import sklearn.metrics
import jieba

    def __init__(self, categories, file_paths):
        if len(categories) != len(file_paths):
            raise Exception('Error: categories and file_paths lengths do not match')
        df_list = []
        for file_ in file_paths:
            df = pd.read_csv(file_, sep="|", header=0)
            df_list.append(df)
        BLDF = pd.concat(df_list)
        BLDF = BLDF.drop_duplicates(subset=['video_title'], keep='first')

        self.categories = len(categories)
        self.videos = len(BLDF)
        self.dataframe = BLDF
        self.D2Vmodels = {}
short = ['233','555','666','哦哦','噢噢','哈哈','喔喔',"啊啊",'？','！','。']
stopwords = [' ',',','啊','啊啊','啊啊','哈','哈哈','。','？','！']
        self._emoticons = []

emoticons = pd.read_csv('emoticons.txt', index_col=None, names=None).iloc[:, 0].tolist()

    def add_emoticons(self, emoticon):
        """Manually add an emoticon"""
        if emoticon not in self._emoticons:
            self._emoticons = self._emoticons.append(emoticon)
stopwords = pd.read_csv('ChineseStopwords', header = None, delimiter="\t",
                        quoting=3, error_bad_lines=False).loc[:,0].tolist()

    def add_stopwords(self, stopword):
        if stopword not in self._stopwords:
            self._emoticons = self._emoticons.append(stopword)

    def _find_all_emot(self, emot, bulletstr, start=0, sub=None, lstps=None):
        if not lstps:
            lstps = []
        if not sub:
            sub = bulletstr
        if emot not in sub:
            return lstps
        elif start >= len(bulletstr) - 1:
            return lstps
        else:
            subpos = sub.find(emot)
            pos = start + subpos
            end = pos + len(emot)
            lstps.append((pos, end))
            start = pos + 1
            sub = bulletstr[start:]
            lst_sub = self._find_all_emot(emot, bulletstr, start, sub, lstps)
            return lstps

def smart_cut(string, patterns, user_dict=None, stopwords=None, short=None):
    def shorten(string, short):
        for s in short:
            if string.startswith(s):
                return s
        return string

    output = []
    str_start = 0

    if isinstance(string, str):
        all_positions = sum([_find_all_emot(emot, string) for emot in patterns], [])
        all_positions.sort()

        if user_dict:
            jieba.load_userdict(user_dict)

        if not all_positions:
            output = jieba.lcut(string)

        else:
            for pos in all_positions:
                str_end = pos[0]
                words_list = jieba.lcut(string)[str_start:str_end]
                if stopwords:
                    words_list = [word for word in words_list if word not in stopwords]
                if short:
                    words_list = [shorten(word, short) for word in words_list]

                output += words_list
                output.append(string[pos[0]:pos[1]])
                str_start = pos[1]

    return output

def smart_cut_corpus(user_dict=None):
    dataframe['normalized_words'] = dataframe['BS_text'].apply(smart_cut,
                                                               patterns=_emoticons,
                                                               user_dict=user_dict,
                                                               short=_short)
