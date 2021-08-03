
#!/usr/bin/python
# -*- coding: utf-8 -*-
import csv,re,os
import nagisa # library used for Natural Language Processing for japanese
import pykakasi # library for conversion of Kanji into Hirigana, Katakana and Romaji
import heapq # library for implementing priority queues where the queue item with higher weight is given more priority in processing
from jamdict import Jamdict # library for searching the japanese vocabulary

from eCSiteReviewCrawler import ReviewAPI # function for getting EC site review and store data in csv file




class SumAPI: 
    def __init__(self):
        self.__csvFile = ''     
        self.__csvPath = './comm'

    def getText(self):
        text=''
        with open('{0}/{1}'.format(self.__csvPath,self.__csvFile), 'r', encoding='UTF-8', errors='ignore') as cf:
            reader = csv.reader(cf)
            header = next(reader)
            for row in reader:
                if not row: continue
                if row[6] == 'N/A': continue
                if (float(row[6]) < 3.0): continue
                text += row[1] if row[1][-1] == '。' else row[1]+'。'

        return re.sub(r"\s+",' ',text) # for removing the extra spaces


    def getToken(self):
        text = self.getText()

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


    def getWeightWordFq(self):
        tokenised_words = self.getToken()
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
    def getSpaceSeperatedJpWords(self, text):
        wakati = pykakasi.wakati()
        conv = wakati.getConverter()
        result_with_spaces = conv.do(text)
        return result_with_spaces
    
    def getSentScore(self): 
        word2count = self.getWeightWordFq()
        print(word2count)
        sentences = self.getText().split("。")
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
    
    def reviewSum(self):
        # get review from EC site
        reviewAPI = ReviewAPI()
        reviewAPI.reviewCrawler()
        arrFiles = [f for f in os.listdir(self.__csvPath) if os.path.isfile(os.path.join(self.__csvPath, f))]
        try:
            with open('summary.txt', 'w', encoding='UTF-8', errors='ignore') as sf:
                for cf in arrFiles :
                    self.__csvFile = cf        
                    best_sentences = self.getSentScore()
                    # join those sentence to form the summary
                    summary = [''.join(b)+'。' for b in best_sentences]

                    print(''.join(summary))                    
                    # sf.write(cf)
                    sf.writelines(summary)
        except Exception as e:
            print('[{1}] Error : {0}'.format(e, SumAPI.reviewSum.__name__))





if __name__ == '__main__':
    # init summerize API
    sumAPI = SumAPI()  
    sumAPI.reviewSum()
        
