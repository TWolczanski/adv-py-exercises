import urllib.request
import urllib.parse
import bs4
import re
import queue
import threading

def find_sentences(content):
    soup = bs4.BeautifulSoup(content, "html.parser")
    # a sentence is starting with a capital letter and ending with a dot, a question mark or an exclamation mark
    sentence_re = re.compile(r"[A-Z][^\.\?\!]*[\.\?\!]")
    python_re = re.compile(r"(((^Python)|(^\"Python\")|( Python)|( \"Python\")|(\"[^\"]* Python\")|( \(Python\))|(\([^\)]* Python\)))([\.\?\!]|([,:]? )))|((^\"Python)|( \"Python)[,:]? .*\")|((^\(Python)|( \(Python)[,:]? .*\))")
    res = []
    # stripped_string is a generator yielding text from HTML tags
    for string in soup.stripped_strings:
        for sentence in sentence_re.finditer(string):
            if python_re.search(sentence.group()):
                res.append(sentence.group())
    return res

# encode non-ascii characters occuring in the link
def quote_link(link):
    scheme, netloc, path, query, fragment = urllib.parse.urlsplit(link)
    path = urllib.parse.quote(path, safe="/%")
    query = urllib.parse.quote(query, safe="/%")
    fragment = urllib.parse.quote(fragment, safe="/%")
    return urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))

# I'm fetching and processing links in breadth-first order using queues
# which are thread-safe data structures (https://docs.python.org/3/library/queue.html)
def crawl(start_page, depth, action):
    global links, contents, THREADS_COUNT
    max_depth = depth
    start_page = quote_link(start_page)
    # a set of already processed links
    processed = set()
    link_re = re.compile(r"^\S*$")
    links.put((start_page, 0))
    processed.add(start_page)
    # count how many pages are left
    counter = 1
    
    # it would probably be possible to parallelize this loop too
    # but it performs CPU-bound tasks, so using the "threading" library would not speed up the program due to GIL
    while counter > 0:
        # consume content
        element = contents.get(block=True)
        counter -= 1
        # an error occured in one of the threads
        if element is None:
            continue
        url, content, depth = element
        soup = bs4.BeautifulSoup(content, "html.parser")
        yield (url, action(content))
        if depth < max_depth:
            # find all "proper" links on the website
            pages = (link.get("href") for link in soup.find_all("a", href=link_re))
            for p in pages:
                # p may be a relative link, so I join it with the base url
                # if p is an absolute link, urljoin will not try to join it
                p = urllib.parse.urljoin(url, quote_link(p))
                # no links will be processed twice
                if p not in processed:
                    processed.add(p)
                    # produce link
                    links.put((p, depth + 1))
                    counter += 1
    # stop the threads by making them consume None
    for _ in range(THREADS_COUNT):
        links.put(None)

def get_content():
    global links, contents
    while True:
        # consume link
        element = links.get(block=True)
        if element is None:
            break
        url, depth = element
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as page:
                content = page.read().decode("utf-8")
            # produce content
            contents.put((url, content, depth))
        except Exception as e:
            print(str(e))
            contents.put(None)

# stores tuples (url, depth)
links = queue.Queue()
# stores tuples (url, content, depth)
contents = queue.Queue()

THREADS_COUNT = 10

threads = [threading.Thread(target=get_content) for _ in range(THREADS_COUNT)]
for t in threads:
    t.start()
page = "https://github.com/TWolczanski/linux-autoscroll"
for x in crawl(page, 1, find_sentences):
    print(x)
print()

threads = [threading.Thread(target=get_content) for _ in range(THREADS_COUNT)]
for t in threads:
    t.start()
page = "https://zapisy.ii.uni.wroc.pl/courses/kurs-rozszerzony-jezyka-python-202122-zimowy"
for x in crawl(page, 1, find_sentences):
    print(x)
print()

# this can take long time to finish
# threads = [threading.Thread(target=get_content) for _ in range(THREADS_COUNT)]
# for t in threads:
#     t.start()
# page = "https://code.visualstudio.com/docs/languages/python"
# for x in crawl(page, 1, find_sentences):
#     print(x)
# print()

threads = [threading.Thread(target=get_content) for _ in range(THREADS_COUNT)]
for t in threads:
    t.start()
page = "https://sites.google.com/cs.uni.wroc.pl/boehm/python_parsing"
for x in crawl(page, 1, find_sentences):
    print(x)