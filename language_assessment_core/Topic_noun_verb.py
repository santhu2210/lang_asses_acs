"""
To identify the topic of the given docuemnt based on the common tokens
"""
import os
import pandas as pd
import nltk
import numpy as np
np.random.seed(2018)
nltk.download('wordnet')

BASE_DIR_PATH = os.path.dirname(os.path.abspath(__file__))


class Topic_noun_verb:
    def term_extraction(self, doc):
        """
        Computes the topic level of the doc based on the topic db
        :param doc: content of the document
        :return: level of the doc w.r.t topic
        """
        noun = []
        verb = []
        for token in doc:
            # print(token, token.pos_, token.is_stop)
            if ((token.pos_ == 'NOUN') & (token.is_stop == False)):
                noun.append(token.lemma_)
            if ((token.pos_ == 'VERB') & (token.is_stop == False)):
                verb.append(token.lemma_)

        verb_set = list(set(verb))
        noun_set = list(set(noun))
        term_set = verb_set + noun_set

        xml_noun = os.path.join(BASE_DIR_PATH, 'MWE', 'topic-noun_all.xlsx')
        difficult_noun = pd.read_excel(open(xml_noun, 'rb'), sheet_name='Final Diff topics')
        inter_noun = pd.read_excel(open(xml_noun, 'rb'), sheet_name='Final inter topics')
        easy_noun = pd.read_excel(open(xml_noun, 'rb'), sheet_name='Final easy topics')

        difficult_key_noun = difficult_noun['keywords'].values.tolist()
        inter_key_noun = inter_noun['keywords'].values.tolist()
        easy_key_noun = easy_noun['keywords'].values.tolist()

        xml_verb = os.path.join(BASE_DIR_PATH, 'MWE', 'topic-verb_all.xlsx')
        difficult_verb = pd.read_excel(open(xml_verb, 'rb'), sheet_name='Final Diff topics')
        inter_verb = pd.read_excel(open(xml_verb, 'rb'), sheet_name='Final inter topics')
        easy_verb = pd.read_excel(open(xml_verb, 'rb'), sheet_name='Final easy topics')

        difficult_key_verb = difficult_verb['keywords'].values.tolist()
        inter_key_verb = inter_verb['keywords'].values.tolist()
        easy_key_verb = easy_verb['keywords'].values.tolist()

        difficult_key = list(set(difficult_key_verb + difficult_key_noun))
        inter_key = list(set(inter_key_noun+inter_key_verb))
        easy_key = list(set(easy_key_noun+easy_key_verb))

        common_diff_lt = [value for value in term_set if value in difficult_key]
        common_inter_lt = [value for value in term_set if value in inter_key]
        common_easy_lt = [value for value in term_set if value in easy_key]

        common_diff = common_diff_lt.__len__()
        common_inter = common_inter_lt.__len__()
        common_easy = common_easy_lt.__len__()

        common_diff = common_diff/(difficult_key.__len__())
        common_inter = common_inter/(inter_key.__len__())
        common_easy = common_easy/(easy_key.__len__())

        print(common_easy, common_inter, common_diff)
        Level = 0
        if ((common_easy > common_inter) & (common_easy > common_diff)):
            Level = 1
            print("Easy")
        elif ((common_inter > common_easy) & (common_inter > common_diff)):
            Level = 2
            print("Inter")
        elif ((common_diff > common_easy) & (common_diff > common_inter)):
            Level = 3
            print("Difficult")
        else:
            Level = 2
        return Level
