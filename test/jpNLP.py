#!/usr/bin/python
# -*- coding: utf-8 -*-
# summerize commend from amazon
import csv,re
import spacy

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

from janome.analyzer import Analyzer
from janome.charfilter import UnicodeNormalizeCharFilter, RegexReplaceCharFilter
from janome.tokenizer import Tokenizer as JanomeTokenizer  # sumyのTokenizerと名前が被るため
from janome.tokenfilter import POSKeepFilter, ExtractAttributeFilter


LANGUAGE = "japanese"
SENTENCES_COUNT = 5

nlp = spacy.load('ja_ginza')


def getText():
    text = ''
    with open('comm\Fuji_Medical_Equipment_Co.,_Ltd._Foot_Massager_-_FT-100.csv', 'r', encoding='UTF-8', errors='ignore') as cf:
        reader = csv.reader(cf)
        header = next(reader)
        for row in reader:
            if not row: continue
            if row[7] == 'N/A': continue
            if (float(row[7]) < 3.0): continue
            # clean_text = row[1].lower()
            # clean_text = re.sub(r"\W"," ",clean_text) # removing any non-words characters which include special characters, comma, punctuation
            # clean_text = re.sub(r"\s+",' ',clean_text) # removing any extra spaces in middle 
            # clean_text = re.sub(r"^\s",' ',clean_text) # removing any extra spaces in beginning
            # clean_text = re.sub(r"\s$",' ',clean_text) # removing any extra spaces in end
            # text += clean_text
            # text.append(clean_text)
            text += row[1] if row[1][-1] == '。' else row[1]+'。'
    return text


def getCorpusByJanome():
    corpus = []
    sents = getText()

    # ()「」、。は全てスペースに置き換える
    char_filters = [UnicodeNormalizeCharFilter(
    ), RegexReplaceCharFilter(r'[(\)「」、。.\s;?!\'`｀＾]', ' ')]
    tokenizer = JanomeTokenizer()
    # 名詞・形容詞・副詞・動詞の原型のみ
    token_filters = [POSKeepFilter(
        ['名詞', '形容詞', '副詞', '動詞']), ExtractAttributeFilter('base_form')]
    analyzer = Analyzer(char_filters= char_filters,tokenizer= tokenizer,token_filters= token_filters)
    corpus = [' '.join(analyzer.analyze(s))+ '。' for s in sents]
    # for sents in corpus:
    #     print(sents)
    return corpus

def getCorpusByGinza():
    corpus = []
    originals = []
    text = getText()
    
    doc = nlp(text)
    for s in doc.sents:
        originals.append(s)
        tokens = []
        for t in s:
            tokens.append(t.lemma_)
        corpus.append(' '.join(tokens))
    return corpus, originals


def summerizedText():
    # 連結したcorpusを再度tinysegmenterでトークナイズさせる    
    corpus, originals = getCorpusByGinza()

    # corpus = getCorpusByJanome()
    parser = PlaintextParser.from_string(
        ' '.join(corpus), Tokenizer(LANGUAGE))

    # stemmer = Stemmer(LANGUAGE)
    # summarizer = Summarizer(stemmer)
    
    summarizer = LexRankSummarizer()
    # summarizer.stop_words = get_stop_words(LANGUAGE)
    summarizer.stop_words = [" ","あそこ","あっ","あの","あのかた","あの人","あり","あります","ある","あれ","い","いう","います","いる","う","うち","え","お","および","おり","おります","か","かつて","から","が","き","ここ","こちら","こと","この","これ","これら","さ","さらに","し","しかし","する","ず","せ","せる","そこ","そして","その","その他","その後","それ","それぞれ","それで","た","ただし","たち","ため","たり","だ","だっ","だれ","つ","て","で","でき","できる","です","では","でも","と","という","といった","とき","ところ","として","とともに","とも","と共に","どこ","どの","な","ない","なお","なかっ","ながら","なく","なっ","など","なに","なら","なり","なる","なん","に","において","における","について","にて","によって","により","による","に対して","に対する","に関する","の","ので","のみ","は","ば","へ","ほか","ほとんど","ほど","ます","また","または","まで","も","もの","ものの","や","よう","より","ら","られ","られる","れ","れる","を","ん","何","及び","彼","彼女","我々","特に","私","私達","貴方","貴方方"]  # スペースも1単語として認識されるため、ストップワードにすることで除外する

    # sentencres_countに要約後の文の数を指定します。
    return summarizer(document=parser.document, sentences_count=SENTENCES_COUNT), originals,corpus


if __name__ == '__main__':
    summaryTexts,originals,corpus = summerizedText()
    # 元の文を表示
    for sentence in summaryTexts:
        # print(sentence)
        print(originals[corpus.index(sentence.__str__())])
