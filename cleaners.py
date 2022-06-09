import re

def cleanText(text, language):
    if(language in ['Hindi', 'hindi', 'hin']):
        # replacing Hindi period with English period
        text = re.sub(r"[।\|]", ".", text, 0, re.MULTILINE)
        # add split tag for punctuation <__>
        text = re.sub(r" *\. *", ".<__>", text, 0, re.MULTILINE)
        text = re.sub(r" *[,!?] *", "<__>", text, 0, re.MULTILINE)
        # remove unknown characters
        text = re.sub(r"[+\“\”\"\'\`\-\dA-Za-z]", "", text, 0, re.MULTILINE)
        # replace split tag with \n
        text = re.sub(r"<__>", "\n", text, 0, re.MULTILINE)
        # remove single character lines
        text = re.sub(r"\n[\.]", "", text, 0, re.MULTILINE)
        # replace multiple newlines
        text = re.sub(r"[\n]+", "\n\n", text, 0, re.MULTILINE)
        # removing extra spaces
        text = re.sub(r"\n ", "\n", text, 0, re.MULTILINE)
    elif(language in ['English', 'english', 'eng']):
        # add split tag for punctuation <__>
        # using negative lookahead (https://www.regular-expressions.info/lookaround.html)
        # text = re.sub(r" *[,!?.](?!\n) *", "\n", text, 0, re.MULTILINE)
        # text = re.sub(r" *[,!?.] *", "", text, 0, re.MULTILINE)
        text = re.sub(r"[\[\(\)\]\"\”\“\…]", "",text, 0, re.MULTILINE)
        text = re.sub(r"\.{2,}", " ",text, 0, re.MULTILINE)
        text = re.sub(r"[\;\:]", "\n",text, 0, re.MULTILINE)
        text = re.sub(r"[\n]+", "\n\n", text, 0, re.MULTILINE)
    return text

def cleanTextForPath(path, outpath, language):
    with open(path, 'r') as f:
        text = f.read()
    text = cleanText(text, language)
    with open(outpath, 'w') as f:
        f.write(text)

