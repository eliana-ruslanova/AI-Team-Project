import pandas as pd
import re
import numpy as np
import nltk
import json as json
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from joblib import load
import sys

input_file = sys.argv[1]   # input file
output_file = sys.argv[2]   # output file
model_file = sys.argv[3]    # benefits.joblib

input = pd.read_json(input_file)
model = load(model_file)

wnl = WordNetLemmatizer()
words = stopwords.words("english")

count = 0

def get_benefits(abstract):

    # in case no abstract is given
    if len(abstract) == 0:
        return ""

    # preprocessing
    sentences = nltk.tokenize.sent_tokenize(abstract)
    all_sentences = list()
    sentence_index = 0
    header = "None"
    benefits = list()

    for sentence in sentences:

        # determine in which section the sentence is (or "None")
        sentence = sentence.replace("</b>", ":")
        colon_split = sentence.lower().split(":")
        if (len(colon_split) > 1):
            if (colon_split[0].__contains__("background") or (colon_split[0].__contains__("purpose"))):
                header = "Background"
            elif (colon_split[0].__contains__("methods") or (colon_split[0].__contains__("main body"))):
                header = "Methods"
            elif (colon_split[0].__contains__("results")):
                header = "Results"
            elif (colon_split[0].__contains__("conclusion")):
                header = "Conclusions"

        # determine position of sentence in text
        sentence_index += 1
        position = (round((sentence_index / (len(sentences))) * 100)) / 100

        # check if sentence contains numbers
        numericals = 0
        numericals_bool = bool(re.search(r'\d', sentence))
        if (numericals_bool):
            numericals = 1

        sentence_data = [sentence, header, position, numericals]
        all_sentences.append(sentence_data)

    df = pd.DataFrame(all_sentences, columns=["sentence", "header", "position", "numericals"])
    df["cleaned"] = df["sentence"].apply(lambda x: " ".join(
        [wnl.lemmatize(i) for i in re.sub("[^a-zA-Z]", " ", re.sub("\%", " percent", x)).split() if
         i not in words]).lower())


    # benefits extraction
    X_predict = df[["cleaned", "header", "position", "numericals"]]
    y_predict = model.predict(X_predict)
    results = model.predict_proba(X_predict)
    df["predicted_label"] = y_predict
    df["proba_0"] = results[:, 0]
    df["proba_1"] = results[:, 1]

    # postprocessing
    label_df = df.loc[(df.predicted_label == 1)]
    labels = label_df.predicted_label.size
    # if 0 sentences were predicted, include the sentence with the highest probability
    if (labels == 0):
        benefits.append(df.nlargest(1, columns=["proba_1"]).sentence.values[0])
    # if more than 3 sentences were predicted, include the 3 sentences with the highest probability
    elif (labels > 3):
        candidates = label_df.nlargest(3, columns=["proba_1"]).sort_values("position")
        for sentence in candidates["sentence"].unique():
            benefits.append(sentence)
    else:
        for sentence in label_df["sentence"].unique():
            benefits.append(sentence)

    # remove headers from start of sentence
    i = 0
    while (i < len(benefits)):
        colon_split = benefits[i].split(":")
        if (len(colon_split) > 1):
            if (colon_split[0].lower().__contains__("background") or colon_split[0].lower().__contains__("purpose")
                    or colon_split[0].lower().__contains__("methods") or colon_split[0].lower().__contains__(
                        "main body")
                    or colon_split[0].lower().__contains__("results") or colon_split[0].lower().__contains__(
                        "conclusion")):
                benefits[i] = benefits[i].replace(colon_split[0] + ":", "").lstrip()
        i += 1

    return " ".join(benefits)

input["Benefits"] = "None"
#input["Benefits"] = input.apply(lambda row: get_benefits(row["Abstract"]), axis=1)
input.loc[input["Research_Type"] == "Research", "Benefits"] = input.loc[input["Research_Type"] == "Research"].apply(lambda row: get_benefits(row["Abstract"]), axis=1)

input.to_json(output_file)

