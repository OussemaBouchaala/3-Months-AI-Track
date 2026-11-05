# Scratchpad: type anything here to test an idea while you read.
# "Try it in the editor" on a lesson example puts it here and runs it.
import re
SIZE = 400       # characters per chunk for fixed-size chunking
OVERLAP = 80  
def chunk_fixed(text, size=SIZE, overlap=OVERLAP):
    """Cut text into pieces of `size` characters. Each piece starts `size - overlap` characters
    after the previous one, so neighbours share `overlap` characters.
    Stop once a piece reaches the end of the text. Empty text -> [].
    Example: chunk_fixed("abcdefghij", 4, 1) -> ["abcd", "defg", "ghij"]"""
    # TODO
    step = size - overlap
    start= 0
    chunks=[]
    while(start+size<len(text)):
        chunks.append(text[start:start+size])
        start= start+step
    chunks.append(text[start:])
    return chunks
def split_by_heading(markdown):
    """Split a Markdown document on lines that start with "## ".
    Return a list of (heading, body) tuples: heading without the "## ", body stripped.
    Text before the first "## " heading is ignored (it's the title and intro)."""
    # TODO: re.split(r"^## ", markdown, flags=re.M) is a good start
    parts=re.split(r"^## ", markdown, flags=re.M)
    result= [part.split("\n", maxsplit=1) for part in parts[1:] ]
    return result
print(chunk_fixed("urrrfhebck ebceuj cjhevcj dcejhvc ye ce",4,1))
print(split_by_heading("""hbkbv 
## lenbcuizevc 
defefefefefef
## rfdvfvdf
regvrgvrg"""))
