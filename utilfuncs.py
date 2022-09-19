import pandas as pd
import re

def testfunc():
	print('test')
    
STOPTAGS = ['#datascience', '#datascientist', '#datascientists','#data']
from nltk.corpus import stopwords
STOPWORDS = stopwords.words('english')
STOPWORDS.extend(['amp','data','science','scientist','scientists',
                  'rt','gt','fyi','imo','imho','tldr'])

def counthashtag(df_in, n_rows = 25):
    '''
    Parameters
    ----------
    df_in : dataframe with a column named 'hashtag'
    n_rows : The default is 20.
    Returns data frame of hashtags and counts
    '''
    hashtags = dict() #pd.DataFrame(columns=['hashtag','count'])
    #hashtags.set_index('hashtag')
    
    tweetnum = df_in.shape[0]
    hashtag_column = df_in['hashtags'].to_list()
    
    for i in range(tweetnum):
        if type(hashtag_column[i]) is str:
            tmptaglist = (hashtag_column[i].lower()).split()
            
            for tmptag in tmptaglist:
                if (tmptag not in STOPTAGS):
                    if (tmptag not in hashtags.keys()): #initialize
                        hashtags[tmptag] = 0
                    hashtags[tmptag] = hashtags[tmptag]+1
    col1 = hashtags.keys()
    col2 = hashtags.values()
    
    df_out = pd.DataFrame({'hashtag':col1, 'count':col2})
    df_out.sort_values(by = 'count', ascending=False, inplace=True)
    
    return df_out.head(n_rows)


def find_keywords(textdata,wordlist):
    '''
    helper function for contains_hashtag
    '''
    flag = 0
    if type(textdata) is str:
        textdata = textdata.lower()
        textdata = textdata.split()
        for w in wordlist:
            if w.lower() in textdata:
                flag = 1
                return flag
    return flag


def contains_hashtag(df_in, search_tag):
    '''
    input: data frame with a hashtag column; a string of hashtag to search for
    output: a filtered dataframe
    '''
    df_in['has_keyword'] = df_in['hashtags'].apply(find_keywords, 
                    **{'wordlist':[search_tag]} )
    df_out = df_in[df_in['has_keyword']==1]
    return df_out
    
                

def countwords(df_in, n_rows = 25):
    '''
    Parameters
    ----------
    df_in : dataframe with a column named 'tweets_processed'
    n_rows : The default is 20.
    Returns data frame of words and counts
    '''
    hashtags = dict() #pd.DataFrame(columns=['hashtag','count'])
    #hashtags.set_index('hashtag')
    
    tweetnum = df_in.shape[0]
    hashtag_column = df_in['tweets_processed'].to_list()
    
    for i in range(tweetnum):
        if type(hashtag_column[i]) is str:
            tmptaglist = (hashtag_column[i].lower())
            tmptaglist = re.sub('[,.!?@|;:#/$%^&*=~()-]', ' ', tmptaglist)
            tmptaglist = tmptaglist.split()
            
            for tmptag in tmptaglist:
                if (tmptag not in STOPWORDS):
                    if (tmptag not in hashtags.keys()): #initialize
                        hashtags[tmptag] = 0
                    hashtags[tmptag] = hashtags[tmptag]+1
    col1 = hashtags.keys()
    col2 = hashtags.values()
    
    df_out = pd.DataFrame({'hashtag':col1, 'count':col2})
    df_out.sort_values(by = 'count', ascending=False, inplace=True)
    
    return df_out.head(n_rows)
