#!/usr/bin/env python
# coding: utf-8

import pickle
import argparse
import spacy
from pyfiglet import Figlet

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

def load_model():
    '''
    Loads the previous created model.
    '''
    with open('../model/model.p', 'rb') as f:
        m = pickle.load(f)
    return m

def load_bow():
    '''
    Loads the previous created bag-of-words.
    '''
    with open('../model/bow.p', 'rb') as f:
        bow = pickle.load(f)
    return bow

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Classifies lyric string and predicts artist')
    figlet = Figlet(font="graffiti")
    print(figlet.renderText('Lyrics Classifier 9000'))
    print("Loading spaCy model. This may take a couple of seconds.")
    nlp = spacy.load("en_core_web_md", disable=["parser", "textcat", "ner"])
    m = load_model()
    bow = load_bow()

    while True:
        print("Please input lyrics:")
        user_input = str(input())
        result = m.predict(bow.transform([user_input]))[0]
        args = parser.parse_args()
        print(f"This string would have been most likely sung by:")
        print(f"{figlet.renderText(result)}")
