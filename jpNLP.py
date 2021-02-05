import csv
import spacy
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer


nlp = spacy.load('ja_ginza')

text = ''
with open('comm\Fuji_Medical_Equipment_Co.,_Ltd._Foot_Massager_-_FT-100.csv', 'r', encoding='UTF-8', errors='ignore') as cf:
    reader = csv.reader(cf)
    header = next(reader)
    for row in reader:
        if not row: continue
        if row[7]=='N/A':continue
        if (float(row[7]) < 3.0): continue
        text += row[1]


corpus = []
originals = []
doc = nlp(text)
for s in doc.sents:
    # print(s.text, s.start_char, s.end_char, s.label_)
    originals.append(s)
    tokens = []
    for t in s:
        tokens.append(t.lemma_)
    corpus.append(' '.join(tokens))


# 連結したcorpusを再度tinysegmenterでトークナイズさせる
parser = PlaintextParser.from_string(''.join(corpus), Tokenizer('japanese'))

summarizer = LexRankSummarizer()
summarizer.stop_words = [' ']  # スペースも1単語として認識されるため、ストップワードにすることで除外する

# sentencres_countに要約後の文の数を指定します。
summary = summarizer(document=parser.document, sentences_count=3)
print(summary)
# 元の文を表示
# for sentence in summary:
#     print(originals[corpus.index(sentence.__str__())])
