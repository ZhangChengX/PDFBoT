#-*- encoding:utf-8 -*-
import os
import re
import json
from copy import deepcopy
from bs4 import BeautifulSoup
from . import Segmentation

# CurrentWorkingDirectory = os.getcwd()

# filter text and combine text
def processText(textPath, outputfile):
    qaList = []
    wrong_answer = []
    qaDict = {}
    rightChoice = ''
    with open(textPath) as fp:
        for line in fp:
            line = line.strip()
            # check if line start with a number
            if line[0].isdigit():
                try:
                    # print("line = " + str(line.split('  ')))
                    qaIndex = line.split('  ')[0]
                    question = line.split('  ')[1].split(' :')[0]
                    qaAnswer = line.split('  ')[1].split(' :')[1]
                    rightChoice = qaAnswer
                    # print("line = "+str(line.split('  ')))
                    # print("line = " + qaIndex+" : "+qaAnswer)
                    qaDict["type"] = "choice"
                    qaDict["question"] = question
                    pass
                except:
                    print('line = '+ line)
                    print('text path = '+textPath)
                # qaIndex = line.split('  ')[0]
                # question = line.split('  ')[1].split(' :')[0]
                # qaAnswer = line.split('  ')[1].split(' :')[1]
                # rightChoice = qaAnswer
                # # print("line = "+str(line.split('  ')))
                # # print("line = " + qaIndex+" : "+qaAnswer)
                # qaDict["type"] = "choice"
                # qaDict["question"] = question
            if line.startswith('A)'):
                if rightChoice == 'A':
                    qaDict["right_answer"] = line.split(') ')[1]
                    pass
                else:
                    wrong_answer.append(line.split(') ')[1])
                    pass
            if line.startswith('B)'):
                if rightChoice == 'B':
                    qaDict["right_answer"] = line.split(') ')[1]
                    pass
                else:
                    wrong_answer.append(line.split(') ')[1])
                    pass
            if line.startswith('C)'):
                if rightChoice == 'C':
                    qaDict["right_answer"] = line.split(') ')[1]
                    pass
                else:
                    wrong_answer.append(line.split(') ')[1])
                    pass
            if line.startswith('D)'):
                if rightChoice == 'D':
                    qaDict["right_answer"] = line.split(') ')[1]
                    pass
                else:
                    wrong_answer.append(line.split(') ')[1])
                    pass
                qaDict["wrong_answer"] = wrong_answer
                # print("qaDict = "+ str(qaDict))
                qaList.append(deepcopy(qaDict))
                qaDict.clear()
                wrong_answer.clear()

    jstr = json.dumps(qaList, indent=4)
    print('jstr = '+jstr)
    f = open(outputfile, 'w')
    f.write(jstr)
    f.close()
    # with open(outputfile, 'w') as outfile:
    #     json.dump(qaList, outfile)


def segment_by_sentence(text, lang):
    sentences_list = []
    if lang == 'zh':
        # RE_SENTENCE_CN = re.compile('(\S.+?[.!?;~。！？；～])|(\S.+?)(?=[\n]|$)')
        RE_SENTENCE_CN = re.compile('(\S.+?[?!;~。？！；～])|(\S.+?)(?=[\n]|$)')
        for match in RE_SENTENCE_CN.finditer(text):
            sentences_list.append( match.group() )
        # seg = Segmentation.SentenceSegmentation(delimiters=util.sentence_delimiters_cn)
    else:
        seg = Segmentation.SentenceSegmentationEn()
        sentences_list = seg.segment(text)
    return sentences_list

def getFileName(path):
    return os.path.basename(path)

def parseStrNodeFromDiv(divSoup):
    strList = []
    nodeList = []
    # print('len = '+str(len(divSoup.div.contents)))
    # for i in divSoup.div.contents:
    #     print('contents = '+str(i))
    print('div soup =='+str(divSoup))
    # print('div soup find div == '+str(divSoup.find('div')))
    print('div soup find div == ' + str(divSoup))
    for j in divSoup.find_all(recursive=False):
        # check if previousSibling is html element
        if bool(BeautifulSoup(str(j.previousSibling), "html.parser").find()):
            strList.append('')
            pass
        else:
            strList.append(j.previousSibling)
        nodeList.append(j)
        # print("previous string = " + str(j.previousSibling))
        # print("j = " + str(j))
        pass
    strList.append(nodeList[-1].nextSibling)
    return strList, nodeList

def getStartIndex(strList, sentence):
    startIndex = 0
    for i, item in enumerate(strList):
        # print('i = '+ str(i))
        # print('item = '+ str(item))
        if sentence.replace(' ','').startswith(item.replace(' ','')):
            startIndex = i
        else:
            continue
    print('start index = '+ str(startIndex))
    return startIndex

def getEndingIndex(strList, sentence):
    endingIndex = 0
    for i, item in reversed(list(enumerate(strList))):
        # print('i = ' + str(i))
        # print('item = ' + str(item))
        if sentence.replace(' ','').endswith(item.replace(' ','')):
            endingIndex = i
        else:
            continue
    print('ending index = '+str(endingIndex))
    return endingIndex

def createNewFirstDiv(soup, sentence):
    print('soup 0001 = '+str(soup))
    strList, nodeList = parseStrNodeFromDiv(soup)
    print("strlist = " + str(strList))
    print("nodelist = " + str(nodeList))
    startIndex = getStartIndex(strList, sentence)
    # soup = BeautifulSoup("<div></div>", 'html.parser')
    soup.clear()
    innerSoup = BeautifulSoup("<span></span>", 'html.parser')
    innerSoup.span['style'] = "background-color:lightblue"
    for i in range(len(nodeList)):
        # print('i = '+str(i))
        if i <startIndex:
            soup.insert(len(soup.contents), strList[i])
            soup.insert(len(soup.contents), nodeList[i])
        else:
            innerSoup.span.insert(len(innerSoup.span.contents),strList[i])
            innerSoup.span.insert(len(innerSoup.span.contents), nodeList[i])
    innerSoup.span.insert(len(innerSoup.span.contents), strList[i+1])
    soup.insert(len(soup.contents), innerSoup)
    print(soup.prettify())
    return soup

def createNewLastDiv(soupEnd, sentence):
    strListEnd, nodeListEnd = parseStrNodeFromDiv(soupEnd)
    print("last strlist  = " + str(strListEnd))
    print("last nodelist = " + str(nodeListEnd))
    endingIndex = getEndingIndex(strListEnd, sentence)
    # soup = BeautifulSoup("<div></div>", 'html.parser')
    soupEnd.clear()
    print('soupEND = '+str(soupEnd))
    innerSoup = BeautifulSoup("<span></span>", 'html.parser')
    innerSoup.span['style'] = "background-color:lightblue"
    for i in range(len(nodeListEnd)):
        # print('i = ' + str(i))
        if i <= endingIndex:
            innerSoup.span.insert(len(innerSoup.span.contents), strListEnd[i])
            innerSoup.span.insert(len(innerSoup.span.contents), nodeListEnd[i])

        else:
            soupEnd.insert(len(soupEnd.div.contents), strListEnd[i])
            soupEnd.insert(len(soupEnd.div.contents), nodeListEnd[i])

    # print('len of contents = '+str(len(soup.div.contents)))
    # print('string i + 1 = '+str(strListEnd[i+1]))
    # print('soup div = '+ str(soup.div))

    soupEnd.insert(len(soupEnd.contents), strListEnd[i+1])
    soupEnd.insert(0, innerSoup)
    print(soupEnd.prettify())
    return soupEnd


if __name__ == '__main__':
    # pattern = 'a'
    # print('pattern01 = '+str(pattern))
    # pattern = pattern[2:]
    # print('pattern02 = '+str(pattern))
    divText = "<div class=\"t m0 x0 h8 y171 ff1 fs5 fc0 sc0 ls0 ws0\">minutes.<span class=\"_ _6\"> </span>Moreover<span class=\"_ _3\"></span>,<span class=\"_ _6\"> </span>the<span class=\"_ _4\"> </span><span class=\"_ _4\"> </span>specialized<span class=\"_ _6\"> </span>VW<span class=\"_ _4\"> </span>is<span class=\"_ _4\"> </span>on<span class=\"_ _6\"> </span>average</div>"
    divtextEnd = '<div class="t m0 x0 h8 y172 ff1 fs5 fc0 sc0 ls0 ws0">35%<span class="_ _b"> </span>faster<span class="_ _b"> </span>than<span class="_ _b"> </span>our<span class="_ _4"> </span>system,<span class="_ _b"> </span>and<span class="_ _b"> </span>never<span class="_ _4"> </span>twice<span class="_ _b"> </span>as<span class="_ _b"> </span>fast.<span class="_ _b"> </span>These</div>'
    sentence = 'Moreover, the highly specialized VW is on average35% faster than our system, and never twice as fast. '
    soup = BeautifulSoup(divText,'html.parser')
    soupEnd = BeautifulSoup(divtextEnd, 'html.parser')

    print('text soup = ' + str(soup))
    createNewFirstDiv(soup,sentence)
    # createNewLastDiv(soupEnd,sentence)