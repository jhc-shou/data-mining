#!/usr/bin/python
# -*- coding: utf-8 -*-
# summerize commend from amazon
import csv,re
import spacy
import mojimoji
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from janome.analyzer import Analyzer
from janome.charfilter import UnicodeNormalizeCharFilter, RegexReplaceCharFilter
from janome.tokenizer import Tokenizer as JanomeTokenizer  # sumyのTokenizerと名前が被るため
from janome.tokenfilter import POSKeepFilter, ExtractAttributeFilter

from nltk.tokenize.util import is_cjk


nlp = spacy.load('ja_ginza')


def cjk_substrings(string):
    i = 0
    while i<len(string):
        if is_cjk(string[i]):
            start = i
            while is_cjk(string[i]): i += 1
            yield string[start:i]
        i += 1

def getText():
    sents = ''
    with open('comm\Fuji_Medical_Equipment_Co.,_Ltd._Foot_Massager_-_FT-100.csv', 'r', encoding='UTF-8', errors='ignore') as cf:
        reader = csv.reader(cf)
        header = next(reader)
        for row in reader:
            if not row:
                continue
            if row[7] == 'N/A':
                continue
            if (float(row[7]) < 3.0):
                continue
            # sents.append(row[1])
            sents += re.sub(r'[(\)「」、。.\s;?!]+', ' ',mojimoji.zen_to_han(row[1],kana=False) )
    return sents


def getCorpus():
    corpus = []
    sents = getText()

    # # ()「」、。は全てスペースに置き換える
    # char_filters = [UnicodeNormalizeCharFilter(
    # ), RegexReplaceCharFilter(r'[(\)「」、。.!]', ' ')]
    # tokenizer = JanomeTokenizer()
    # # 名詞・形容詞・副詞・動詞の原型のみ
    # token_filters = [POSKeepFilter(
    #     ['名詞', '形容詞', '副詞', '動詞']), ExtractAttributeFilter('base_form')]
    # analyzer = Analyzer(char_filters= char_filters,tokenizer= tokenizer,token_filters= token_filters)
    # corpus = [' '.join(analyzer.analyze(s))+ '。' for s in sents]
    # for sents in corpus:
    #     print(sents)

    doc = nlp(sents)
    for s in doc.sents:
        # print(s.sents, s.start_char, s.end_char, s.label_)
        tokens = []
        for t in s:
            tokens.append(t.lemma_)
        corpus.append(' '.join(tokens))
    return corpus


def summerizedText():
    # 連結したcorpusを再度tinysegmenterでトークナイズさせる
    corpus = getCorpus()
    parser = PlaintextParser.from_string(
        ''.join(corpus), Tokenizer('japanese'))

    summarizer = LexRankSummarizer()
    summarizer.stop_words = [' ']  # スペースも1単語として認識されるため、ストップワードにすることで除外する

    # sentencres_countに要約後の文の数を指定します。
    return summarizer(document=parser.document, sentences_count=3)


if __name__ == '__main__':
    summaryTexts = summerizedText()
    # 元の文を表示
    for sentence in summaryTexts:
        print(sentence)
