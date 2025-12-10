import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # init empty distribution {}
    prob_distr = {p: 0 for p in list(corpus.keys())}
    
    # number of links in page
    N = len(corpus[page])
    # number of pages
    M = len(corpus)

    rand_page = (1 - damping_factor) / M

    # check if page contains links
    if N > 0:
        # for each link calc. probability
        rand_link = damping_factor / N
        for l in corpus[page]:
            prob_distr[l] += rand_link
        # calculate probability of selecting a random page
        for p in corpus:
            prob_distr[p] += rand_page
    # if no links, select page at random (by assuming page is linked to all pages including itself) 
    else:
        rand_link = damping_factor / M
        for p in corpus:
            prob_distr[p] += rand_link + rand_page
    return prob_distr


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys())
    freqs = {p: 0 for p in pages}
    current = random.choice(pages)

    freqs[current] += 1

    if n < 1:
        raise Exception("Sample must be greater than 1")
    for _ in range(n - 1):
        distr = transition_model(corpus, current, damping_factor)
        # Sample according to the probability distribution
        current = random.choices(list(distr.keys()), weights=list(distr.values()))[0]
        freqs[current] += 1
    pagerank = {p: freqs[p] / n for p in pages}

    return pagerank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys())
    N = len(pages)
    ranks = {p: 1 / N for p in pages}
    converged = False
    while not converged:
        new_ranks = {}
        for p in pages:
            base = (1 - damping_factor) / N
            contrib = 0
            for q in pages:
                # If q links to no pages, treat it as linking to all pages
                if len(corpus[q]) == 0:
                    contrib += ranks[q] / N
                elif p in corpus[q]:
                    contrib += ranks[q] / len(corpus[q])
            new_ranks[p] = base + damping_factor * contrib
        # Check convergence
        converged = all(abs(new_ranks[p] - ranks[p]) < 0.001 for p in pages)
        ranks = new_ranks
    return ranks


if __name__ == "__main__":
    main()
