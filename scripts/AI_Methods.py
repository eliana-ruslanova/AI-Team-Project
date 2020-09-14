from anytree import Node, RenderTree
import pandas as pd
import numpy as np
import json
import codecs
import re
import sys

input_file = sys.argv[1]        # input file
output_file = sys.argv[2]       # output file
hierarchy_file = sys.argv[3]    # ai_hierarchy.txt


# build tree
with codecs.open(hierarchy_file, "r", encoding="utf8") as f_in:
    hierarchy = f_in.read().split("\n")
    nodes = list()
    lvl = 0

    for term in hierarchy:
        values = term.split(" | ")
        lvl = values[0].count("\t")
        values[0] = values[0].replace("\t", "")
        values[1] = values[1].replace("\r", "")
        kws = set()
        if (values[1] == ""):
            keyword = values[0].replace("-", " ").lower()
            if (keyword[-1] == "s"):
                keyword = keyword[0:-1]
            kws.add(keyword)
        else:
            kws_list = values[1].split(",")
            for kw in kws_list:
                kws.add(kw)
        node = Node(values[0], keywords=kws, level=lvl, count=0)
        nodes.append(node)

    index1 = 0
    for node in nodes:
        children = list()
        index2 = index1
        while (index2 < len(nodes) - 1):
            index2 += 1
            if (nodes[index2].level == node.level + 1):
                children.append(nodes[index2])
            elif (nodes[index2].level < node.level):
                break
        if (children):
            nodes[index1].children = children
        index1 += 1
f_in.close()

#for pre, _, node in RenderTree(nodes[0]):
#    print("%s%s" % (pre, node.name))

# returns path of node as string
def get_path(node):
    out = ""
    for ancestor in node.ancestors:
        out = out + str(ancestor.name) + "/"
    out = out + str(node.name)
    return out


def find_methods(text, nodes):

    # find minimal set of nodes for methods that appear (do not include node when more specific node is found)
    methods = set()
    last_node = nodes[-1]
    for node in reversed(nodes):
        for keyword in node.keywords:
            if text.__contains__(keyword):
                node.count = node.count+1
                if not (node in last_node.ancestors):
                    methods.add(node)
                    last_node = node

    # turn list of nodes into list of paths
    paths = []
    if (methods):
        for method in methods:
            paths.append(get_path(method))

    return ", ".join(paths)



input = pd.read_json(input_file)
input["preprocessed"] = input["Title"] + input["Abstract"] + input["Keywords_Merged"]
input["preprocessed"] = input["preprocessed"].apply(lambda x: re.sub("\W", " ", x.lower()))
input["Methods"] = input.apply(lambda row: find_methods(row["preprocessed"], nodes), axis=1)
input = input.drop(columns=["preprocessed"])
input.to_json(output_file)
