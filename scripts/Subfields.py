import pandas as pd
import numpy as np
import json
import re
import sys
from joblib import load
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


input_file = sys.argv[1]    # input file
output_file = sys.argv[2]   # output file
model_file = sys.argv[3]   # diagnosis_prognosis.joblib

model = load(model_file)
input = pd.read_json(input_file)


class Subfield:

    def __init__(self, name, keywords):
        self.name = name
        self.keywords = keywords


def categorise(text, categories, cleaned):

    # in case no abstract is given
    if len(text) == 0:
        return "None"

    subfield_list = []
    for category in categories:
        for keyword in category.keywords:
            if text.__contains__(str(keyword)):
                if not(subfield_list.__contains__(category.name)):
                    subfield_list.append(category.name)

    if model.predict([cleaned]) == 1:
        subfield_list.append("Diagnosis & Prognosis")

    if len(subfield_list) == 0:
        return "None"

    return ", ".join(subfield_list)


drug_discovery = Subfield("Drug Discovery", ["drug discovery", "drug design", "drug development", "drug resistance", "drug testing", "drug candidate", "biomedical engineering",
                                             "medicinal chemistry", "biopharmaceutic", "toxicogenomic", "toxicology", "compound", "inhibitor", "vaccin", "immunization", "antagonist"])
treatment = Subfield("Treatment", ["treatment", "personali", "therap", "prescription", "patient care", "dosing", "individualiz", "individualis", "rehabilitation",
                                  "intervention"])
epidemiology = Subfield("Epidemiology", ["epidemi", "pandemi", "endemi", "outbreak"])
robotics = Subfield("Robotics", ["robot", "prosthetic", "prostheses", "brain computer interface", "brain-computer interface", " bci", "human-machine interface",
                                "neuromorphic", "gesture recognition"])
smart_healthcare = Subfield("Smart Healthcare", ["smart", "analytics", "data process", "data manag", "data science", "data analy", "internet of things",
                                                 "internet-of-things", "chatbot", "web-based", "mobile phone", "mobile app", "electronic health record", "answering system",
                                                "patient flow", "interoperability", "privacy", "digitali", "smartphone", "user interface", "speech recognition",
                                                 "e-health", "data mining", "data security", "wearable", "health system", "health care system"])
genetics = Subfield("Genetics", ["genom", "allele", "genes", "genetic", "phenotype", "microrna", "mirna", " rna", " dna"])
subfields = [drug_discovery, treatment, epidemiology, robotics, smart_healthcare, genetics]


stemmer = PorterStemmer()
words = stopwords.words("english")

input["cleaned"] = input["Abstract"].apply(lambda x: " ".join([stemmer.stem(i) for i in re.sub("[^a-zA-Z]", " ", x).split() if i not in words]).lower())
input["Subfields"] = input.apply(lambda row: categorise(row["Abstract"], subfields, row["cleaned"]), axis=1)
input = input.drop(columns=["cleaned"])
input_empty = input.loc[input["Subfields"] == "None"]
print(input["Subfields"].size)
print(input_empty["Subfields"].size)
input.to_json(output_file)

