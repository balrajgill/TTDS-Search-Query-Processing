from textwrap import wrap
from typing import Final
import xml.etree.ElementTree as ET
import re
from nltk import PorterStemmer
import pickle
import math

from nltk.util import pr, tokenwrap

ps = PorterStemmer()
text_file = open("stopwords.txt", "r")
stopwords = text_file.read().splitlines()

a_file = open("data.pkl", "rb")
output = pickle.load(a_file)

a_file2 = open("docnums.pkl", "rb")
output2 = pickle.load(a_file2)

doc_to_words_dict = output
docnums = output2




queries = []
with open('queries.boolean.txt') as queryfile:
    queries = queryfile.readlines()
    queries = [((query.rstrip())[2:]) for query in queries]


def single_word(query):
    docs = [key for key in doc_to_words_dict[query].keys()]
    return docs

def and_query(left,right):
    
    #word1 = doc_to_words_dict[left].keys()
    #word2 = doc_to_words_dict[right].keys()
    #andresult = list(set(word1).intersection(word2))
    return list(set(left).intersection(right))
    #return andresult
    
def or_query(left,right):
    #split = list(filter(None,re.split(" OR ",query)))
    #split = [ps.stem(s) for s in split]
    #word1 = doc_to_words_dict[split[0]].keys()
    #word2 = doc_to_words_dict[split[1]].keys()
    #orresult = list(set(word1).union(word2))
    return list(set(left).union(right))


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
    return list(set(final))
       


def phrase(query):
    print(query)
    split = list(filter(None,re.split("[\"\s]",query)))
    split = [ps.stem(s) for s in split]
    word1 = doc_to_words_dict[split[1]].keys()
    word2 = doc_to_words_dict[split[2]].keys()

def parser(q):
    if " " not in q and "#" not in q:
        
        return single_word(ps.stem(q))
    
    

    
    
    elif "AND" in q and "#" not in q:
        split = list(filter(None,re.split(" AND ",q)))
        print("------------------------------------------------")
        print(split)
        #print(and_query(parser(split[0]),parser(split[1])))
        return and_query(parser(split[0]),parser(split[1]))
    elif "#" in q:
         return proximity(q)
    



    elif "OR" in q:
        split = list(filter(None,re.split(" OR ",q)))
        return or_query(parser(split[0]),parser(split[1]))



queryindex = 1    
for q in queries:
    print(str(q) + ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" + str(parser(q)))
    queryindex+=1




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
#a_file = open("data.pkl", "wb")
#pickle.dump(doc_to_words_dict, a_file)
#a_file.close()
