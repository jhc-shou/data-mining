
# All necessary imports
import csv,re
import nagisa # library used for Natural Language Processing for japanese
import pykakasi # library for conversion of Kanji into Hirigana, Katakana and Romaji
import heapq # library for implementing priority queues where the queue item with higher weight is given more priority in processing
import pandas as pd # library for managing the data in form of table
from jamdict import Jamdict # library for searching the japanese vocabulary

def getText():
    text=''
    with open('comm\Fuji_Medical_Equipment_Co.,_Ltd._Foot_Massager_-_FT-100.csv', 'r', encoding='UTF-8', errors='ignore') as cf:
        reader = csv.reader(cf)
        header = next(reader)
        for row in reader:
            if not row: continue
            if row[7] == 'N/A': continue
            if (float(row[7]) < 3.0): continue
            text += row[1] if row[1][-1] == '。' else row[1]+'。'

    return re.sub(r"\s+",' ',text) # for removing the extra spaces


def getToken():
    text = getText()

    # Pre-Processing the japanese data using regex
    clean_text = text.lower() # converts any english word in lower case
    clean_text = re.sub(r"\W"," ",clean_text) # removing any non-words characters which include special characters, comma, punctuation
    clean_text = re.sub(r"\d"," ",clean_text) # removing any digits
    clean_text = re.sub(r"\s+",' ',clean_text) # removing any extra spaces in middle 
    clean_text = re.sub(r"^\s",' ',clean_text) # removing any extra spaces in beginning
    clean_text = re.sub(r"\s$",' ',clean_text) # removing any extra spaces in end

    sentences = text.split("。")

    jp_tokenised_words = nagisa.extract(clean_text, extract_postags=['英単語','接頭辞','形容詞','名詞','動詞','助動詞','副詞'])
    
    return jp_tokenised_words.words


def getWeightWordFq():
    tokenised_words = getToken()
    jp_stopwords = ["あそこ","あっ","あの","あのかた","あの人","あり","あります","ある","あれ","い","いう","います","いる","う","うち","え","お","および","おり","おります","か","かつて","から","が","き","ここ","こちら","こと","この","これ","これら","さ","さらに","し","しかし","する","ず","せ","せる","そこ","そして","その","その他","その後","それ","それぞれ","それで","た","ただし","たち","ため","たり","だ","だっ","だれ","つ","て","で","でき","できる","です","では","でも","と","という","といった","とき","ところ","として","とともに","とも","と共に","どこ","どの","な","ない","なお","なかっ","ながら","なく","なっ","など","なに","なら","なり","なる","なん","に","において","における","について","にて","によって","により","による","に対して","に対する","に関する","の","ので","のみ","は","ば","へ","ほか","ほとんど","ほど","ます","また","または","まで","も","もの","ものの","や","よう","より","ら","られ","られる","れ","れる","を","ん","何","及び","彼","彼女","我々","特に","私","私達","貴方","貴方方"]

    # print(tokenised_words)

    # Calculate the frequency of each word 
    word2count = {} # dictionary stores the word as a key and frequency as its value
    for word in tokenised_words:
        if word not in jp_stopwords:  # We dont want to include any stop word
            word2count[word] = 1 if word not in word2count.keys() else word2count[word]+1
                

    # Calculate the weighted frequency of each word by dividing the frequency of the word by maximum frequency of word in whole article            
    for key in word2count.keys():
        word2count[key] = word2count[key]/max(word2count.values()) # Weighted Frequency
    
    return word2count


# Below function , "getSpaceSeperatedJpWords(text)" inserts spaces among words in Japanese sentence by using 'pykakasi' library
def getSpaceSeperatedJpWords(text):
    wakati = pykakasi.wakati()
    conv = wakati.getConverter()
    result_with_spaces = conv.do(text)
    return result_with_spaces
  
def getSentScore(): 
    word2count = getWeightWordFq()
    sentences = getText().split("。")
    sent2score={} # This dictionary stores each sentence and its score as value
    for sentence in sentences: # for each sentence in all sentences
        # get each word as a token using "'英単語','接頭辞','形容詞','名詞','動詞','助動詞','副詞'" as list of filters
        tokenised_sentence = nagisa.extract(sentence, extract_postags=['英単語','接頭辞','形容詞','名詞','動詞','助動詞','副詞'])
        words = tokenised_sentence.words
        for word in words: # if each word of all words in that sentence and
            if word in word2count.keys(): # if that word is available in "word2count" dictionary
                # add its corresponding weighted freqency
                sent2score[sentence] = word2count[word] if sentence not in sent2score.keys() else sent2score[sentence] + word2count[word]
    print(sent2score)
    return heapq.nlargest(5,sent2score,key=sent2score.get) # top 15 sentences are selected having high scores




if __name__ == '__main__':
    best_sentences =getSentScore()
    # join those sentence to form the summary
    summary = [''.join(b)+'。' for b in best_sentences]

    print(''.join(summary))