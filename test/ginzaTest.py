from collections import defaultdict
from ginza import *
import spacy
import csv

from urllib import request
from bs4 import BeautifulSoup
import bs4
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

nlp = spacy.load("ja_ginza")  # GiNZAモデルの読み込み

# frames = defaultdict(lambda: 0)  # 依存関係の出現頻度を格納
# sentences = set()  # 重複文検出用のset


# with open('comm\Fuji_Medical_Equipment_Co.,_Ltd._Foot_Massager_-_FT-100.csv', 'r', encoding='UTF-8', errors='ignore') as cf:
#     reader = csv.reader(cf)
#     header = next(reader)
#     for row in reader:
#         if not row: continue
#         if row[7]=='N/A':continue
#         if (float(row[7]) < 3.0): continue
#         doc = nlp(row[1])  # 解析を実行し
#         for sent in doc.sents:  # 文単位でループ
#           if sent.text in sentences: continue  # 重複文はスキップ
#           sentences.add(sent.text)
#           for t in bunsetu_head_tokens(sent):  # 文節主辞トークンのうち
#             if t.pos_ not in {"ADJ", "VERB"}: continue  # 述語以外はスキップ
#             v = phrase(lemma_)(t)  # 述語とその格要素(主語・目的語相当)の句を集める
#             dep_phrases = sub_phrases(t, phrase(lemma_), is_not_stop)
#             subj = [phrase for dep, phrase in dep_phrases if dep in {"nsubj"}]
#             obj = [phrase for dep,
#                    phrase in dep_phrases if dep in {"obj", "iobj"}]
#             for s in subj:
#               for o in obj:
#                 frames[(s, o, v)] += 1  # 格要素と述語の組み合わせをカウント


# for frame, count in sorted(frames.items(), key=lambda t: -t[1]):
#   print(count, *frame, sep="\t")  # 出現頻度の高い順に表示



# urlに要約対象とする書籍のURLを指定します。以下は「だしの取り方 by 北大路魯山人」のURLです。
url = 'https://www.aozora.gr.jp/cards/001403/files/49986_37674.html'
html = request.urlopen(url)
soup = BeautifulSoup(html, 'html.parser')
body = soup.select('.main_text')

text = ''
for b in body[0]:
    if type(b) == bs4.element.NavigableString:
        text += b
        continue
    # ルビの場合、フリガナは対象にせずに、漢字のみ使用します。
    text += ''.join([e.text for e in b.find_all('rb')])


print(text)


corpus = []
originals = []
doc = nlp(text)
for s in doc.sents:
    originals.append(s)
    tokens = []
    for t in s:
        tokens.append(t.lemma_)
    corpus.append(' '.join(tokens))

print(len(corpus))
print(len(originals))


# 連結したcorpusを再度tinysegmenterでトークナイズさせる
parser = PlaintextParser.from_string(''.join(corpus), Tokenizer('japanese'))

summarizer = LexRankSummarizer()
summarizer.stop_words = [' ']  # スペースも1単語として認識されるため、ストップワードにすることで除外する

# sentencres_countに要約後の文の数を指定します。
summary = summarizer(document=parser.document, sentences_count=3)

# 元の文を表示
for sentence in summary:
    print(originals[corpus.index(sentence.__str__())])