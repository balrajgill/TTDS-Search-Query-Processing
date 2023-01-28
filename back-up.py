from typing import Final
import xml.etree.ElementTree as ET
import re
from nltk import PorterStemmer
import math
import pickle

ps = PorterStemmer()
text_file = open("stopwords.txt", "r")
stopwords = text_file.read().splitlines()

tree = ET.parse('trec.5000.xml')
root = tree.getroot()
test = []

words = {}
for doc in root:
    words[int(doc.find("DOCNO").text)] = doc.find("HEADLINE").text + doc.find("TEXT").text  
    

for key in words.keys():
    split_sentence = re.split('[^a-zA-Z0-9]',  words[key])
    tokens = list(filter(None, split_sentence))
    stopword_tokens = [word for word in tokens if word not in stopwords]
    stemmed_tokens = []
    for word in stopword_tokens:
        stemmed_tokens.append(ps.stem(word))
    words[key] = stemmed_tokens

doc_to_words_dict = {}

for docnumber in words.keys():
    position = 1
    words_pos_dict = {}
    for token in words[docnumber]:
        if token not in doc_to_words_dict.keys():
            words_pos_dict[docnumber] = [position]
            doc_to_words_dict[token] = words_pos_dict
            position +=1
            words_pos_dict = {}
        else:
            
            if docnumber in doc_to_words_dict[token]:
                doc_to_words_dict[token][docnumber].append(position)
                
            
            else:
                words_pos_dict[docnumber] = [position]
                doc_to_words_dict[token][docnumber] = [position]
            
            position+=1
            words_pos_dict = {}
    position = 1
    
docnums = words.keys()

with open('index.txt', 'w') as f:
    for word in doc_to_words_dict.keys():
        f.write(word + ":" + str(len(doc_to_words_dict[word])) + "\n")
        for docnumber in doc_to_words_dict[word].keys():
            f.write("\t" + str(docnumber) + ": ")
            commmaIndex = 1
            for position in doc_to_words_dict[word][docnumber]:
                if commmaIndex < len(doc_to_words_dict[word][docnumber]):
                    f.write(str(position) + ",")
                else:
                    f.write(str(position))
                commmaIndex+=1
            commmaIndex = 1
            f.write("\n")
f.close()





queries = []
with open('queries.boolean.txt') as queryfile:
    queries = queryfile.readlines()
    queries = [((query.rstrip())[2:]) for query in queries]


def single_word(query):
    docs = [key for key in doc_to_words_dict[query].keys()]
    return docs

def and_query(query):
    split = list(filter(None,re.split(" AND ",query)))
    split = [ps.stem(s) for s in split]
    
    word1 = doc_to_words_dict[split[0]].keys()
    word2 = doc_to_words_dict[split[1]].keys()
    andresult = list(set(word1).intersection(word2))
    print(query + " " + str(andresult))
    
def or_query(query):
    split = list(filter(None,re.split(" OR ",query)))
    split = [ps.stem(s) for s in split]
    word1 = doc_to_words_dict[split[0]].keys()
    word2 = doc_to_words_dict[split[1]].keys()
    orresult = list(set(word1).union(word2))
    print(query + " " + str(orresult))


def proximity(query):
    split = list(filter(None,re.split("#|\s|[\(\)\,]",query)))
    split = [ps.stem(s) for s in split]
    distance = int(split[0])
    word1 = doc_to_words_dict[split[1]].keys()
    word2 = doc_to_words_dict[split[2]].keys()
    andresult = list(set(word1).intersection(word2))
    final = []
    for r in andresult:
       pos1 = doc_to_words_dict[split[1]][r]
       pos2 = doc_to_words_dict[split[2]][r]
       for p1 in pos1:
           for p2 in pos2:
               if abs(p1 - p2) <= distance:
                   final.append(r)
                   break
    print(list(set(final)))
       


def phrase(query):
    split = list(filter(None,re.split("[\"\s]",query)))
    split = [ps.stem(s) for s in split]
    word1 = doc_to_words_dict[split[1]].keys()
    word2 = doc_to_words_dict[split[2]].keys()

def parser(q):
    if " " not in q and "#" not in q:
        print(q + ": " + str(single_word(ps.stem(q))))
    
    
    
    elif "AND" in q and "#" not in q:
        if ("\"" not in q) and ("NOT" not in q):
            and_query(q)
        
    elif "#" in q:
        proximity(q)
    



    elif "OR" in q:
        or_query(q)

    
for q in queries:
    parser(q)

ranked_queries = []       #variables used to store queries read from the query txt file
with open('queries.ranked.txt') as queryfile:              #open the file and start reading
    ranked_queries = queryfile.readlines()      
    for i in range(len(ranked_queries)):                   #loop used to read each line in the file and store it
        ranked_queries[i] = re.split("^\W",ranked_queries[i].strip("\n"))             #split queries by white space and remove newline at end 
        

rankings = []                                        # used to store the 150 top scoring documents for each query 
for query in ranked_queries:                         # loop used to go thorugh each query
    querynumber = int(query[0][:2].strip(" "))       # get query number to be used for writing results to text file
    doc_score_pairs = []                             # used to store document and its score as a tuple with 3 elements (query,docid,score)
    pre_query = []                                   # used to store the query that is tokenised and stop words removed and stemmed
    for element in query:                            # loop through the queries to process each one
        pre_query = element[2:].split()          
        pre_query = [ps.stem(token.strip("?")) for token in pre_query if token not in stopwords]

        
    
    
    
    for docnum in docnums:                           # repeat for each document
        wtd = 0.0                                    # variable for storing thw weight of each query
        for token in pre_query:                      # for each document loop through each word in query and calculate its score 
            df = len(doc_to_words_dict[token].keys())            # number of documents the word appears in 
            if docnum in doc_to_words_dict[token].keys():        # if the word in query is in document the line below is executed
                tf = len(doc_to_words_dict[token][docnum])       
                wtd += (1+ math.log10(tf))*math.log10(5000/df)   
            else :                                               # else if word is not in query then first part of the product becomes 1
                wtd += math.log10(5000/df)
        doc_score_pairs.append((querynumber,docnum,wtd))
    
    doc_score_pairs.sort(key = lambda x: float(x[2]), reverse = True)    #use lambd function to sort the list of tuples using the 3rd element score
    rankings.extend(doc_score_pairs[:150])                               #add the top 150 score for a document for the query to the final list
    
    


with open("results.ranked.txt", "w") as resultsfile:             #write the results of the queries to txt file
    for tuples in rankings:
        resultsfile.write(str(tuples[0]) + "," + str(tuples[1]) + "," + str(tuples[2]) + "\n")

a_file = open("data.pkl", "wb")
pickle.dump(doc_to_words_dict, a_file)
a_file.close()

a_file2 = open("docnums.pkl", "wb")
pickle.dump(list(words.keys()), a_file2)
a_file2.close()
