"""
Computes the grammar and language part which is used by the RSC_main_test_v5 file for testing
"""
import numpy as np
from docx import Document
import pandas as pd
import language_check
import spacy
nlp = spacy.load('en_core_web_sm')

#  start-flag , 0 indicates that the header information of the word doc is under process, 1 indicates abstract is extracted and the grammar process can start


class Grammar_and_Language:
    def __init__(self, file):
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        self.file = file
        # print("Checking grammar and language for ",self.file)

    def grammar(self):
        """
                Identifies the grammar error in the document
                :return: a dataframe with all errors and no of grammar error in the document
        """
        lang_tool = language_check.LanguageTool("en-US")
        # lang_tool.enable_spellchecking()
        statlist1 = []
        statlist2 = []
        total_erroneous_para = 0

        try:
            doc = Document(self.file)
        except Exception as e:
            print("Bad Word Document. The specific error is ", e)

            statlist1.append((self.file, (str(e) + "-->Bad XML format in the word document")))
            statlist2.append((self.file, (str(e) + "-->Bad XML format in the  word document")))

            grmrerr = pd.DataFrame(statlist1, columns=['Document', 'Error Message (if any)'])
            read_score = pd.DataFrame(statlist2, columns=['Document', 'Error Message(if any)'])
            return (grmrerr, read_score)

        for para in doc.paragraphs:
            length = len((para.text).split())
            if ((para.text.startswith('References')) | (para.text.startswith('Notes and references'))):
                break

            if (length < 4):
                continue

            # total_char = total_char + len(para.text)
            try:
                matches = lang_tool.check(para.text)
                matches_cor = lang_tool.correct(para.text)

                error = 0
                for match in matches:
                    # print (match)
                    # if ((match.ruleId != "WHITESPACE_RULE") & (match.ruleId != "COMMA_PARENTHESIS_WHITESPACE")):
                    # if(match.locqualityissuetype == 'grammar'):
                    # if (1):
                    if ((match.locqualityissuetype == 'grammar') |
                            ((match.category == 'Possible Typos') & (match.locqualityissuetype == 'typographical')) |
                            (match.category == 'Punctuation Errors') |
                            ((match.category == 'Redundant Phrases') & (match.locqualityissuetype == 'style')) |
                            ((match.category == 'Miscellaneous') & (match.locqualityissuetype == 'misspelling'))):
                        error = error + 1
                        statlist1.append(
                            ('Document:' + (self.file), match, para.text, matches_cor, ','.join(match.replacements),
                             match.ruleId, match.msg, match.category, match.locqualityissuetype))

                total_erroneous_para = total_erroneous_para + error

            except Exception as e:
                print("exception error--->", e)
                lang_tool = language_check.LanguageTool("en-US")
                matches = lang_tool.check(para.text)
                matches_cor = lang_tool.correct(para.text)

                error = 0
                for match in matches:
                    # if ((match.ruleId != "WHITESPACE_RULE") & (match.ruleId != "COMMA_PARENTHESIS_WHITESPACE") & (
                    #         match.ruleId != "EN_UNPAIRED_BRACKETS") & (match.ruleId != "UPPERCASE_SENTENCE_START") & (
                    #         match.ruleId != "THE_SENT_END")):
                    if ((match.locqualityissuetype == 'grammar') |
                            ((match.category == 'Possible Typos') & (match.locqualityissuetype == 'typographical')) |
                            (match.category == 'Punctuation Errors') |
                            ((match.category == 'Redundant Phrases') & (match.locqualityissuetype == 'style')) |
                            ((match.category == 'Miscellaneous') & (match.locqualityissuetype == 'misspelling'))):

                        error = error + 1
                        statlist1.append(
                            ('Document:' + (self.file), match, para.text, matches_cor, ','.join(match.replacements),
                             match.ruleId, match.msg, match.category, match.locqualityissuetype))

                total_erroneous_para = total_erroneous_para + error

        grmrerr = pd.DataFrame(statlist1, columns=['Document', 'Match', 'Wrong Sentences', 'Possible correct sentences',
                                                   'Possible replacements', 'rule violated', 'Message', 'Category',
                                                   'Type'])

        return grmrerr, total_erroneous_para

    def tree_height(self, root):
        """
        Find the maximum depth (height) of the dependency parse of a spacy sentence by starting with its root
        Code adapted from https://stackoverflow.com/questions/35920826/how-to-find-height-for-non-binary-tree
        :param root: spacy.tokens.token.Token
        :return: int, maximum height of sentence's dependency parse tree
        """
        if not list(root.children):
            return 1
        else:
            return 1 + max(self.tree_height(x) for x in root.children)

    def get_average_heights(self, text):
        """
        Computes average height of parse trees for each sentence in paragraph.
        :param paragraph: spacy doc object or str
        :return: float
        """
        if type(text) == str:
            doc = nlp(text)
        else:
            doc = text
        roots = [sent.root for sent in doc.sents]

        return np.mean([self.tree_height(root) for root in roots]), [self.tree_height(root) for root in roots]

    def parse_tree(self, text):
        """
            computes the parse tree height of the given text
            :param text: text of the given document
            :return: average parse tree height, parse tree height of various range
            """
        tmp_avg_prse_tree_height, tmp_perse_height = self.get_average_heights(text)
        avg_prse_tree_height = round(tmp_avg_prse_tree_height, 2)
        perse_height = pd.DataFrame({"perse_tree_len": tmp_perse_height})

        tree_len_less_than_3 = perse_height[perse_height.perse_tree_len < 3].__len__()
        tree_len_between_3_6 = perse_height[
            (perse_height.perse_tree_len >= 3) & (perse_height.perse_tree_len <= 6)].__len__()
        tree_len_between_6_9 = perse_height[
            (perse_height.perse_tree_len >= 6) & (perse_height.perse_tree_len <= 9)].__len__()
        tree_len_greater_than_9 = perse_height[perse_height.perse_tree_len > 9].__len__()

        percnt_len_perse_less_than_3 = tree_len_less_than_3 / len(perse_height) * 100
        percnt_len_perse_between_3_6 = tree_len_between_3_6 / len(perse_height) * 100
        percnt_len__perse_between_6_9 = tree_len_between_6_9 / len(perse_height) * 100
        percnt_len_perse_greater_than_9 = tree_len_greater_than_9 / len(perse_height) * 100

        return avg_prse_tree_height, percnt_len_perse_less_than_3, percnt_len_perse_between_3_6, percnt_len__perse_between_6_9, percnt_len_perse_greater_than_9

    '''
       Distance between subject & ROOT
    '''

    def distnce_sub_root(self, sent):
        """
            Computes distance between the first subject and the main root verb
            :param sent: sentence
            :return: distance between the first subject and the main root verb
            """
        doc = nlp(sent)
        wordcnt = 0
        nrootpos = 0
        nsubcnt = 0
        nsubpos = 0

        for token in doc:
            wordcnt += 1
            if ((token.dep_ == 'ROOT') & (nrootpos == 0)):
                nrootpos = wordcnt
            if ((token.dep_ == 'nsubj') | (token.dep_ == 'nsubjpass') |
                    (token.dep_ == 'csubjpass')) & (nsubcnt == 0):
                nsubpos = wordcnt
                nsubcnt = 1

        distance_sub_rootverb = abs(nrootpos - nsubpos) - 1
        return distance_sub_rootverb


# if __name__ == '__main__':
#         g=Grammar_and_Language("Manuscript.docx")
#         grmrerr, total_erroneous_para=g.grammar()
#         print (total_erroneous_para)
#         grmrerr.to_csv("my.csv")
