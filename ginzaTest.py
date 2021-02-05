from collections import defaultdict
from ginza import *
import spacy
import csv

nlp = spacy.load("ja_ginza")  # GiNZAモデルの読み込み

frames = defaultdict(lambda: 0)  # 依存関係の出現頻度を格納
sentences = set()  # 重複文検出用のset


with open('comm\Fuji_Medical_Equipment_Co.,_Ltd._Foot_Massager_-_FT-100.csv', 'r', encoding='UTF-8', errors='ignore') as cf:
    reader = csv.reader(cf)
    header = next(reader)
    for row in reader:
        if not row: continue
        if row[7]=='N/A':continue
        if (float(row[7]) < 3.0): continue
        doc = nlp(row[1])  # 解析を実行し
        for sent in doc.sents:  # 文単位でループ
          if sent.text in sentences: continue  # 重複文はスキップ
          sentences.add(sent.text)
          for t in bunsetu_head_tokens(sent):  # 文節主辞トークンのうち
            if t.pos_ not in {"ADJ", "VERB"}: continue  # 述語以外はスキップ
            v = phrase(lemma_)(t)  # 述語とその格要素(主語・目的語相当)の句を集める
            dep_phrases = sub_phrases(t, phrase(lemma_), is_not_stop)
            subj = [phrase for dep, phrase in dep_phrases if dep in {"nsubj"}]
            obj = [phrase for dep,
                   phrase in dep_phrases if dep in {"obj", "iobj"}]
            for s in subj:
              for o in obj:
                frames[(s, o, v)] += 1  # 格要素と述語の組み合わせをカウント


for frame, count in sorted(frames.items(), key=lambda t: -t[1]):
  print(count, *frame, sep="\t")  # 出現頻度の高い順に表示
