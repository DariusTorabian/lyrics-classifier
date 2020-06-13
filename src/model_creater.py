#!/usr/bin/env python
# coding: utf-8

'''
This module creates a Multinominal Naive Bayes model from given JSON inputs
and saves the model locally.
'''
import argparse
import pickle
import en_core_web_md
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn import metrics
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from pyfiglet import Figlet


def read_lyrics_to_df(filename, artistname):
    '''
    Reads a previous scraped and saved json file with lyrics into a dataframe
    and appends artistname to artists_list for later use.
    '''
    df = pd.read_json(filename)
    df["artist"] = artistname
    if artistname not in artists_list:
        artists_list.append(artistname)
    df = pd.concat([lyrics_df, df], axis=0)
    return df

def custom_tokenizer(text):
    """
    converts a string into a text of tokens using spacy 
    """
    tokens = []
    for t in nlp(text):
        if not(len(t) < 2 or t.is_stop or t.like_num or 
               t.is_punct or t.is_oov or not t.is_alpha):
            tokens.append(t.lemma_)
    return tokens 

def create_model(filepathlist, artistlist):
    '''
    Creates a NB-model & Bag-of-words and saves them locally.
    '''
    lyrics_df = pd.DataFrame()
    for fp, a in zip(filepathlist, artistlist):
        lyrics_df = pd.concat([lyrics_df, read_lyrics_to_df("../data/"+str(fp), str(a))])
    y = lyrics_df["artist"]
    X = lyrics_df["lyrics"]

    bow = CountVectorizer(tokenizer=custom_tokenizer,
                          ngram_range=(1, 3), 
                          min_df=0.01, 
                          max_df=0.99)
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    X_train = bow.fit_transform(X_train)
    X_test = bow.transform(X_test)

    m = Pipeline([
        ('TfIdf', TfidfTransformer()),
        ('NB', MultinomialNB())
    ])
    m.fit(X_train, y_train)

    with open('../model/bow.p', 'wb') as f:
        pickle.dump(bow, f)
    with open('../model/model.p', 'wb') as f:
        pickle.dump(m, f)
    print(f"Test acc:{metrics.accuracy_score(y_test, m.predict(X_test))}")
    print(f"Train acc:{metrics.accuracy_score(y_train, m.predict(X_train))}")

    
    print(figlet.renderText('Model successfully created'))
    return

if __name__ == "__main__":

    artists_list = []
    lyrics_df = pd.DataFrame()
    filepathlist = []
    artistlist = []

    parser = argparse.ArgumentParser(description='Creates a model from lyrics .json files')
    args = parser.parse_args()
    figlet = Figlet(font="graffiti")
    print(figlet.renderText('Lyrics Model Creat0r 9000')) 
    dictionary_result = {"filepath":[], "artist":[]}
    loop = True

    while loop == True:
        print("Please input the filename of the .json lyrics file (e.g. 'artist.json'):")
        filepath = input()
        print("Whats the name of the artist?")
        artist = input()

        filepathlist.append(filepath)
        artistlist.append(artist)
        print(filepathlist)
        print(artistlist)

        answer = None
        while answer not in ("yes", "no"):
            answer = input("Do you want to add another lyrics file? Enter yes or no: ")
            if answer == "yes":
                continue
            elif answer == "no":
                loop = False
                break
            else:
                print("Please enter 'yes' or 'no'.")
    print("Please wait a moment while the model is created.")
    nlp = en_core_web_md.load(disable=["parser", "textcat", "ner"])
    create_model(filepathlist, artistlist)
