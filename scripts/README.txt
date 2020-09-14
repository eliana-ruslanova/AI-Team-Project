README:

- all three scripts can be called from the command line with the command:
python file_name argument1 argument2 argument3

- the first two arguments are always the name of the input file and the name of the output file

- the third argument is dependent on each file:
	- diagnosis_prognosis.joblib for Subfields.py
	- ai_hierarchy.txt for AI_Methods.py
	- benefits.joblib for Benefits_extraction.py

- the order of execution does not matter, but for the benefits extraction it is important that 
the research type classification was already executed and stored in a column named "Research_Type"

- the following python imports are used:

import pandas
import numpy
import json 
import codecs
import re
import sys
from joblib import load
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem import PorterStemmer
from anytree import Node
