import pandas as pd
import gensim
import sklearn
import sklearn.metrics
import jieba
import wordcloud
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

class Bilibili:
    def __init__(self, cat_path_dict):
        df_list = []
        for cat, path in cat_path_dict.items():
            df = pd.read_csv(path, sep="|", header=0)
            df_list.append(df)
        BLDF = pd.concat(df_list)
        BLDF = BLDF.drop_duplicates(subset=['video_title'], keep='first')

        self.cat_dict = cat_path_dict
        self.dataframe = BLDF
        self.D2Vmodels = {}
        self._short = ['233','555','666','哦哦','噢噢','哈哈','喔喔',"啊啊",'？','！','。']
        self._stopwords = [' ',',','啊','啊啊','啊啊','哈','哈哈','。','？','！']
        self._emoticons = []

    def categories(self):
        """
        Return currently available video categories
        """
        return self.cat_dict.keys()

    def number_of_categories(self):
        """
        Return the number of video categories in the database
        """
        return len(self.cat_dict)

    def number_of_videos(self):
        """
        Return the number of videos in the databse
        """
        return len(self.dataframe)

    def topk_videos_by_cat(self, main_category, sub_category=None, topk=5):
        """
        Return top k videos in specified category
        """
        if sub_category:
            return self.dataframe[(self.dataframe['main category']==main_category)&
                                  (self.dataframe['sub category']==sub_category)][:topk]
        else:
            return self.dataframe[self.dataframe['main category']==main_category][:topk]

    def load_emoticons(self, file_path):
        """
        Load emoticons from a specified txt file
        """
        self._emoticons += pd.read_csv(file_path, index_col=None, names=None).iloc[:, 0].tolist()

    def add_emoticons(self, emoticon):
        """
        Manually add an emoticon
        """
        if emoticon not in self._emoticons:
            self._emoticons.append(emoticon)

    def load_stopwords(self, file_path):
        """
        Load emoticons from a specified txt file
        """
        self._stopwords += pd.read_csv(file_path, header=None, delimiter="\t",
                                       quoting=3, error_bad_lines=False).loc[:,0].tolist()

    def add_stopword(self, stopword):
        """
        Add a stopword to stopwords list (for text processing)
        """
        if stopword not in self._stopwords:
            self._emoticons.append(stopword)

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

    def save_D2V_model(self, fname, model_name):
        """
        Save D2V model for later use
        """
        self.D2Vmodels[model_name].save(fname)

    def finish_training_D2V_model(self, model_name):
        """
        Finish training a model (=no more updates, only querying) to trim unneeded model memory.
        """
        self.D2Vmodels[model_name].delete_temporary_training_data(keep_doctags_vectors=True, keep_inference=True)

    def avail_D2V_model(self):
        """
        Return a list of currently available D2V models
        """
        return self.D2Vmodels.keys()

    def load_D2V_model(self, model_name, fname):
        """
        Load saved D2V model
        """
        D2Vmodel = gensim.models.doc2vec.Doc2Vec.load(fname)
        self.D2Vmodels[model_name] = D2Vmodel

    def topk_similar_videos(self, video_name, model_name, topk=5):
        """
        Find top k similar videos based on similarity between the content
        of bullet screens (using a specified Doc2Vec model)
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

    def topk_similar_videos_by_keywords(self, keywords, model_name, topk=5):
        """
        Find top k similar videos based on similarity between the content
        of bullet screens and user-entered keywords (using a specified Doc2Vec model)
        """
        output = []
        D2Vmodel = self.D2Vmodels[model_name]
        if isinstance(keywords, str):
            keywords = [keywords]
        inferred_vector = D2Vmodel.infer_vector(keywords).reshape(1, -1)
        for index, row in self.dataframe.iterrows():
            v = row['video_title']
            url = row['video_url']
            cat = row['main category'] + "/" + row['sub category']
            tagVec = D2Vmodel.docvecs[v].reshape(1, -1)
            sim_score = sklearn.metrics.pairwise.cosine_similarity(
                tagVec, inferred_vector)[0][0]
            output.append((v, cat, url, sim_score))

        output.sort(key=lambda x: x[3], reverse=True)
        output = output[1:topk + 1]

        output_df = pd.DataFrame({'Video Title': [x[0] for x in output],
                                  'Category': [x[1] for x in output],
                                  'URL': [x[2] for x in output],
                                  'Similarity': [x[3] for x in output]})
        output_df = output_df[['Video Title', 'Category', 'URL', 'Similarity']]

        return output_df


    def generate_wordcloud(self, main_category, sub_category=None, max_words=100, font_path=None,
                           savefig=False, figname='wordcloud'):
        """
        Generate a word cloud of the specified video category.
        """
        if sub_category:
            tokens= self.dataframe[(self.dataframe['main category'] == main_category)
                                   &(self.dataframe['sub category'] == sub_category)]['normalized_words'].sum()
        else:
            tokens = self.dataframe[self.dataframe['main category'] == main_category]['normalized_words'].sum()

        wc = wordcloud.WordCloud(font_path=font_path,
                                 background_color="white",
                                 max_words=max_words,
                                 width=1000, height=1000, mode='RGBA',
                                 scale=.5).generate(" ".join(tokens))
        plt.imshow(wc)
        plt.axis("off")
        if savefig:
            figname = figname + ".pdf"
            plt.savefig(figname, format='pdf')
        plt.show()
