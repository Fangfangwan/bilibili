import pandas as pd
import gensim
import sklearn
import sklearn.metrics
import jieba


class Bilibili:
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
        self._short = ['233','555','666','哦哦','噢噢','哈哈','喔喔',"啊啊",'？','！','。']
        self._stopwords = [' ',',','啊','啊啊','啊啊','哈','哈哈','。','？','！']
        self._emoticons = []

    def load_emoticons(self, file_path):
        """Load emoticons from a specified txt file"""
        self._emoticons = pd.read_csv(file_path, index_col=None, names=None).iloc[:, 0].tolist()

    def add_emoticons(self, emoticon):
        """Manually add an emoticon"""
        if emoticon not in self._emoticons:
            self._emoticons = self._emoticons.append(emoticon)

    def load_stopwords(self, file_path):
        """Load emoticons from a specified txt file"""
        self._stopwords = pd.read_csv(file_path, header = None, delimiter="\t",
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

    def smart_cut(self, string, patterns, user_dict=None, stopwords=None, short=None):
        def shorten(string, short):
            for s in short:
                if string.startswith(s):
                    return s
            return string

        output = []
        str_start = 0

        if isinstance(string, str):
            all_positions = sum([self._find_all_emot(emot, string) for emot in patterns], [])
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

    def smart_cut_corpus(self, user_dict=None):
        self.dataframe['normalized_words'] = self.dataframe['BS_text'].apply(self.smart_cut,
                                                                             patterns=self._emoticons,
                                                                             user_dict=user_dict,
                                                                             short=self._short)

    def generate_D2V_model(self, model_name, size):
        """
        Generate a D2V model of specified size
        """
        taggedDocs = []
        for index, row in self.dataframe.iterrows():
            docKeywords = []  # s for s in keywords if s in row['normalized_words']
            docKeywords.append(row['video_title'])
            docKeywords.append(row['category'])
            taggedDocs.append(gensim.models.doc2vec.LabeledSentence(words=row['normalized_words'], tags=docKeywords))
        D2Vmodel = gensim.models.doc2vec.Doc2Vec(taggedDocs, size=size)
        self.D2Vmodels[model_name] = D2Vmodel

    def save_D2V_model(self, model_name):
        """
        Save D2V model for later use
        """
        self.D2Vmodels[model_name].save(model_name)

    def load_D2V_model(self, model_name):
        """
        Load saved D2V model
        """
        D2Vmodel = gensim.models.doc2vec.Doc2Vec.load(model_name)
        self.D2Vmodels[model_name] = D2Vmodel

    def topk_similar_videos(self, video_name, model_name, topk=10):
        """
        find top k similar
        """
        output = []
        D2Vmodel = self.D2Vmodels[model_name]
        for index, row in self.dataframe.iterrows():
            v = row['video_title']
            url = row['video_url']
            cat = row['main category'] + "/" + row['sub category']
            tagVec = D2Vmodel.docvecs[v].reshape(1, -1)
            sim_score = sklearn.metrics.pairwise.cosine_similarity(
                tagVec, D2Vmodel.docvecs[video_name].reshape(1, -1))[0][0]
            output.append((v, cat, url, sim_score))

        output.sort(key=lambda x: x[3], reverse=True)
        output = output[1:topk + 1]

        output_df = pd.DataFrame({'Video Title': [x[0] for x in output],
                                  'Category': [x[1] for x in output],
                                  'URL': [x[2] for x in output],
                                  'Similarity': [x[3] for x in output]})
        output_df = output_df[['Video Title', 'Category', 'URL', 'Similarity']]

        return output_df


##############################Test##################################

#load data
#cats = ['动画','娱乐','时尚','游戏','生活','科技','音乐','鬼畜','影视']

#file_paths = ['/Users/lingdai/Documents/Bilibili/BLData动画.txt',
#              '/Users/lingdai/Documents/Bilibili/BLData娱乐.txt',
#              '/Users/lingdai/Documents/Bilibili/BLData时尚.txt',
#              '/Users/lingdai/Documents/Bilibili/BLData游戏.txt',
#              '/Users/lingdai/Documents/Bilibili/BLData生活.txt',
#              '/Users/lingdai/Documents/Bilibili/BLData科技.txt',
#              '/Users/lingdai/Documents/Bilibili/BLData音乐.txt',
#              '/Users/lingdai/Documents/Bilibili/BLData鬼畜.txt',
#              '/Users/lingdai/Documents/Bilibili/BLData影视.txt']

#testBL = Bilibili(categories=cats, file_paths=file_paths)
#print(testBL.dataframe[:1])
#print("")

#data processing
#testBL.load_emoticons('/Users/lingdai/Documents/emoticons.txt')
#testBL.load_stopwords('/Users/lingdai/Downloads/ChineseStopwords.txt')
#testBL.smart_cut_corpus(user_dict='/Users/lingdai/Downloads/BilibiliWords.txt')
#
#testBL.generate_D2V_model('Bilibili7000', size=7000)

#print(testBL.topk_similar_videos('【五五开】在下挂逼，有何贵干', 'Bilibili7000', topk=10))
#print(testBL.topk_similar_videos('【渣渣辉】我是贪玩小辉', 'Bilibili7000', topk=10))
#print(testBL.topk_similar_videos('【更新1p，告别蝴蝶袖】美丽芭蕾 天鹅臂 累断手','Bilibili7000', topk=10))
