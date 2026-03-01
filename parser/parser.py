import nltk
from nltk.tree import Tree
import sys
import re
from nltk.tokenize import word_tokenize

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP
S -> NP VP Conj NP VP
NP -> N | Det N 
NP -> Det Adj N | Det Adj Adj N | Det Adj Adj Adj N 
NP -> NP PP  
NP -> NP Conj NP
VP -> V | V NP
VP -> VP PP
VP -> VP PP NP
VP -> VP Adv | Adv VP
VP -> VP Conj VP
PP -> P | P NP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    token_bank = []

    # s = word_tokenize(sentence)
    s = re.split(r"[^\w]+", sentence)
    for t in s:
        if any(char.isalpha() for char in t):
            token_bank.append(t.lower())

    return token_bank

def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    chunk = []

    def traverse(node):
        if not isinstance(node, Tree):
            return
        
        # Base case
        if node.label() == "NP" and not contains_np(node):
            chunk.append(node)
            return
        
        # Recursive case
        for child in node:
            traverse(child)

    traverse(tree)
    return chunk

def contains_np(tree):
    return any(
        subtree.label() == "NP" 
        for subtree in tree.subtrees() 
        if subtree != tree
        )



if __name__ == "__main__":
    main()
