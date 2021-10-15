#!/usr/bin/env python
# coding: utf-8
import wget
from unidecode import unidecode
from datetime import datetime
import json
import os
import subprocess
from copy import deepcopy

import cssutils
from bs4 import BeautifulSoup

from text_util.text_util import segment_by_sentence
from text_util.util import replaceSpecialUnicode
import urllib3

# CurrentWorkingDirectory = os.getcwd()

output_path = "output"
externalPath='/Users/quanquandiandian/Sites/www/output'


def isCSStext(text):
    flag = False
    texts = text.splitlines()
    for txt in texts:
        if txt.startswith('.'):
            return True
    return flag

# return a list of css
def getCSStext(path):
    cssText = []
    htmlfile = open(path, 'r', encoding='utf-8')
    htmlhandle = htmlfile.read()
    # soup = BeautifulSoup(str(htmlhandle), 'html.parser').find(name='style', type='text/css').find_all(recursive=False)
    soup = BeautifulSoup(str(htmlhandle), 'html.parser').find_all(name='style')

    for style in soup:
        # print("soup = " + str(style))
        if isCSStext(str(style)):
            cssText.append(str(style))

    return cssText
    pass


def getValueOfClass(cssTexts):
    classDict = {}
    for cssText in cssTexts:
        sheet=cssutils.parseString(cssText.replace('<style type="text/css">','').replace('</style>',''))
        for rule in sheet:
            try:
                if rule.selectorText.startswith('.x'):
                    for property in rule.style:
                        if property.name == 'left':
                            classDict[rule.selectorText[1:]]=float(property.value.replace('px',''))
                if rule.selectorText.startswith('.h'):
                    for property in rule.style:
                        if property.name == 'height':
                            classDict[rule.selectorText[1:]]=float(property.value.replace('px',''))
                if rule.selectorText.startswith('.y'):
                    for property in rule.style:
                        if property.name == 'bottom':
                            classDict[rule.selectorText[1:]]=float(property.value.replace('px',''))
                if rule.selectorText.startswith('.fs'):
                    for property in rule.style:
                        if property.name == 'font-size':
                            classDict[rule.selectorText[1:]]=float(property.value.replace('px',''))
            except:
                pass
        # print('class dict = ' + str(classDict))
    return classDict

# return a list of page div
def getSoup(path):
    htmlfile = open(path, 'r', encoding='utf-8')
    htmlhandle = htmlfile.read()
    soup = BeautifulSoup(str(htmlhandle), 'html.parser').find(name='div', id='page-container').find_all(recursive=False)
    # print('num of children soup = '+ str(len(soup)))
    return soup

# convert list of class to a dic of class
# class = ['t', 'm0', 'x12', 'h9', 'y5a', 'ff2', 'fs3', 'fc0', 'sc0', 'ls0', 'ws0']
def getDicOfClass(listOfClass):
    dicOfClass ={}
    for item in listOfClass:
        if item.startswith('x'):
            dicOfClass['left']=item
        if item.startswith('h'):
            dicOfClass['height']=item
        if item.startswith('y'):
            dicOfClass['bottom']=item
        if item.startswith('fs'):
            dicOfClass['font-size']=item
    return dicOfClass

# convert list of class to a dic of class
# class = ['t', 'm0', 'x12', 'h9', 'y5a', 'ff2', 'fs3', 'fc0', 'sc0', 'ls0', 'ws0']
def getlistOfTargetClass(listOfClass):
    listOfTargetClass =[]
    for item in listOfClass:
        if item.startswith('x'):
            listOfTargetClass.append(deepcopy(item))
        if item.startswith('h'):
            listOfTargetClass.append(deepcopy(item))
        if item.startswith('y'):
            listOfTargetClass.append(deepcopy(item))
        if item.startswith('fs'):
            listOfTargetClass.append(deepcopy(item))
    # print('target classes = '+str(listOfTargetClass))
    return listOfTargetClass

def getDivDictWithGivenClass(soup, PAGEID):
    classes = []
    listOfDivDict = []
    count = 0      #trace index of text div
    for pageDiv in soup:
        # record the page number
        pageId = pageDiv["data-page-no"]
        # print('page id = '+ pageId)
        lineDivs = pageDiv.find_all(name='div')
        if int(pageId,16) != PAGEID:
            continue
        for line in lineDivs:
            count = count + 1
            divDict = {}
            # print('line = ' + str(line))
            if line.has_attr('class'):
                pass
            else:
                classes.clear()
                continue
            classes.extend(line["class"])
            #filter div by classes
            if len(getDicOfClass(deepcopy(classes)))!=4:
                continue
            if True:
                divDict['count'] = count
                # divDict['class'] = deepcopy(classes)
                divDict['class'] = getDicOfClass(deepcopy(classes))
                divDict['text'] = line.get_text()
                divDict['pageId'] = int(pageId,16)  # convert hex into int
                # print("div dict = "+ str(divDict))
                listOfDivDict.append(divDict)
            classes.clear()

    # for tagdic in listOfDivDict:
    #     jstr = json.dumps(tagdic, indent=4)
    #     jstr = str(tagdic)
    #     print('jstr = ' + jstr)

    return listOfDivDict

def checkSide(divDict, classDict, left, right):
    divLeft = classDict[divDict.get("class").get('left')]
    # print('divLeft = '+ str(divLeft))
    # print('right = '+ str(divLeft))
    if divLeft>=classDict[right]:
        return 'right'
    if divLeft>=classDict[left] and divLeft<classDict[right]:
        return 'left'
    return None

def insertDivToListOfLine(listOfLine, classDict,div,left, right, dist=10):
    tempLine = []
    tempListOfLine = []
    flag = False
    for line in listOfLine:
        if abs(classDict[line[0].get("class").get("bottom")] - classDict[div.get("class").get('bottom')])<dist and (flag == False):
            if checkSide(line[0], classDict, left, right) == checkSide(div, classDict, left, right):
                line.append(div)
                flag = True
        tempListOfLine.append(line)

    if flag==False:
        tempLine.append(div)
        tempListOfLine.append(tempLine)

    return tempListOfLine


def getListOfLine(listOfDivDict,classDict,left, right, dist=10):
    listOfLine=[]  # list of line
    # line=[]  # list of div which would be in same line
    for div in listOfDivDict:
        listOfLine = insertDivToListOfLine(listOfLine,classDict,div,left,right,dist)
    listOfLine = cleanLine(listOfLine,left,right)

    # for ln in listOfLine:
    #     print('-----------')
    #     print('line = '+str(ln))
    #     print('line = '+ getTextFromLine(ln))
    #     # print('-----------')

    return listOfLine

def cleanLine(listOfLine, left, right):
    temp = []
    for line in listOfLine:

        text = getTextFromLine(line)
        if line[0].get('class').get('left') == left or line[0].get('class').get('left') == right:
            temp.append(line)
        else:
            numChar = 0
            numLetter = 0
            for char in text:
                if char.isalpha():
                    numLetter=numLetter+1
                    numChar = numChar + 1
                else:
                    numChar = numChar + 1

            # print('-----------')
            # print('line = ' + str(line))
            # print('line = ' + getTextFromLine(line))
            #
            # print('num char = '+ str(numChar))
            # print('num letter = '+str(numLetter))
            # print('percentage = '+ str(float(numLetter)/float(numChar)))
            # print('is alpha = '+ str(text[0].isalpha())+' '+str(text[0]))
            if float(numLetter)/float(numChar)<0.5 and len(line)<5:
                # print('flag = 1')
                pass
            elif len(line)>5 and float(numLetter)/float(numChar)<0.7:
                # print('flag = 2')
                pass
            elif float(numLetter)/float(numChar)<0.7 and (not text[0].isalpha()):
                # print('flag = 3')
                pass
            else:
                # print('flag = 4')
                temp.append(line)
    return temp

def getTextFromLine(line):
    text = ''
    for div in line:
        text = text + div['text']
    return text

def combinePara(listOfLine, ClassDic, left, right):
    mostFs, lineDist = getMostFrequencyDist(listOfLine, ClassDic)
    # print('line dist = '+str(lineDist))
    page = []   # list of paragraph
    # print('left = '+str(left))
    # print('list line 0 0 left = '+str(listOfLine[0][0].get('class').get('left')))
    flag=True
    if listOfLine[0][0].get('class').get('left') == left:
        para = ''
    else:
        para = '    '

    # print('first para = '+ '1'+str(para)+'1')
    for line in listOfLine:
        if not line:
            continue
        text=getTextFromLine(line)

        # print('line[0] = '+ str(lineDist[str(line[0].get('count'))]))
        # if there are no 'preDist' or 'nextDist' value, set them to 1
        if 'preDist' in lineDist[str(line[0].get('count'))]:
            pass
        else:
            lineDist[str(line[0].get('count'))]['preDist'] = 1

        if 'nextDist' in lineDist[str(line[0].get('count'))]:
            pass
        else:
            lineDist[str(line[0].get('count'))]['nextDist'] = 1

        # check if line is begin with leftmost
        if line[0].get('class').get('left') == left or line[0].get('class').get('left') == right:
            # if ('preDist' in lineDist[str(line[0].get('count'))]) and ('nextDist' in lineDist[str(line[0].get('count'))]):
            #     flag = True
            # else:
            #     flag = False
            # 如果前后距离大于3px， it could be subtitle. 检查line和前后的距离
            if abs(lineDist[str(line[0].get('count'))]['preDist']-mostFs)>3 and abs(lineDist[str(line[0].get('count'))]['nextDist']-mostFs)>3:
                # check if 换列
                if abs(lineDist[str(line[0].get('count'))]['preDist']-mostFs)<400 and abs(lineDist[str(line[0].get('count'))]['nextDist']-mostFs)<400:
                    page.append(para)
                    para = ''
                else:
                    if para.rstrip().endswith('-'):
                        para = para.rstrip()[:-1] + text
                    else:
                        if para == '':
                            para = text
                            # print('empty text = ' + str(text))
                        else:
                            para = para.rstrip() + " " + text
            else:
                if para.rstrip().endswith('-'):
                    para = para.rstrip()[:-1] + text
                else:
                    if para == '':
                        para = text
                        # print('empty text = '+ str(text))
                    else:
                        # print('para = ' + str(para))
                        para = para.rstrip() + " " + text
        # elif classDict.get(getMostFrequencyFS(listOfLine)) > classDict.get(line[0].get('class').get('font-size')) and len(line)==1:
        #         #     page.append(para)
        #         #     pass

        # line没有顶格
        else:
            page.append(para)
            para = text
            # if len(text)>15 and len(line)<10:
            #     page.append(para)
            #     para=text
            # else:
            #     pass

    if para in page:
        pass
    else:
        page.append(para)
    return page

# Newpage is list of line, line is list of txtnodeDict
# key is the key in txtNodeDict
def getMostFreValueOfKey(newpage, key):
    if len(newpage)==0:
        return 0
    if len(newpage)==1:
        return newpage[0][0][key]
    countKey = {}
    for line in newpage:
        value = int(line[0][key])
        if key == 'preSpace' and value<1:
            continue
        if value not in countKey:
            countKey[value] = 1
        else:
            countKey[value] = countKey[value]+1

    return max(countKey, key=countKey.get)

def getMostFrequencyDist(listOfLine, classDict):
    # lineObject{"line": line
    #            "preDist": 和previous line的距离
    #            "nextDist": 和next line的距离
    #            "id": string(str(pageId)+str(count)) unique
    # }
    # linedist{"id":    "preDist":
    #                   "nextDist"
    # }
    #
    #
    listOfLineObject=[]
    lineObject={}
    count={}
    lineDist = {}
    preDist = 1
    aftDist = 1
    fistLine = listOfLine[0]
    # pageId = str(listOfLine[0][0].get('pageId'))
    lastline = listOfLine[-1]
    preLine = listOfLine[0]
    for line in listOfLine:
        if not line:
            continue
        if line == fistLine :

            lineDist[str(line[0].get('count'))]={}
            tempDict = lineDist[str(line[0].get('count'))]
            tempDict['preDist']=preDist
            # print('temp dict = '+ str(tempDict))
            lineDist[str(line[0].get('count'))]=tempDict

            preLine = line

        elif line == lastline:
            lineDist[str(line[0].get('count'))]={}
            tempDict = lineDist[str(line[0].get('count'))]
            tempDict['preDist'] = preDist
            tempDict['nextDist'] = aftDist

            lineDist[str(line[0].get('count'))]= tempDict

            preLine = line


        else:
            lineDist[str(line[0].get('count'))]={}
            tempDict = lineDist[str(line[0].get('count'))]

            preDist=abs(classDict[line[0].get('class').get('bottom')]-classDict[preLine[0].get('class').get('bottom')])

            pretempDict = lineDist[str(preLine[0].get('count'))]
            pretempDict['nextDist'] = preDist
            lineDist[str(preLine[0].get('count'))] = pretempDict

            tempDict['preDist'] = preDist
            lineDist[str(line[0].get('count'))]= tempDict

            preLine = line

            if preDist not in count:
                count[preDist] = 1
            else:
                count[preDist] = count[preDist]+1
    # print('count = ' + str(count))
    # # get the most two classes
    mostFs = max(count, key=count.get)
    # print('fs dist = '+str(mostFs))

    # for line in listOfLine:
    #     print(json.dumps(lineDist[str(line[0].get('count'))], indent=4))
    #     print('line = '+str(line))
    #     print('sent id = '+str(str(line[0].get('count'))))
    #     lineObject['line']= line
    #     lineObject['preDist']=lineDist[str(line[0].get('count'))]['preDist']
    #     # lineObject['nextDist']=lineDist[str(line[0].get('count'))]['nextDist']
    #     lineObject['id']=pageId+'+'+str(line[0].get('count'))
    #     listOfLineObject.append(deepcopy(lineObject))
    # for item in listOfLineObject:
    #     print(json.dumps(item, indent=4))
    #     pass

    return mostFs, lineDist

def getLeftAndRight(listOfDivDict,classDict):
    count = {}
    countFS = {}
    for divDict in listOfDivDict:
        fs = divDict.get('class').get('font-size')
        if fs not in countFS:
            countFS[fs] = 1
        else:
            countFS[fs] = countFS[fs]+1
    basefs = max(countFS, key=countFS.get)

    for divDict in listOfDivDict:
        # if len(line[0]['text'])<5:
        #     print('len = '+str(len(line[0]['text'])))
        #     print('test for left and right  text = '+str(line[0]['text']))
        #     continue
        left = divDict.get('class').get('left')
        # only count the div have the same base front-size
        if divDict.get('class').get('font-size') != basefs:
            continue

        if  left not in count:
            count[left] = 1
        else:
            count[left] = count[left] + 1

    # print('count = '+ str(count))


    # get the most two classes
    most=max(count, key=count.get)
    del count[most]
    # print('count = ' + str(count))
    seMost=max(count, key=count.get)
    # print('most = '+ str(most))
    # print('se most = '+ str(seMost))
    # print('base front-size = '+ str(basefs))
    if classDict[most]<classDict[seMost]:
        return most, seMost, basefs
    else:
        return seMost, most, basefs

def printDiv(listOfdiv):
    for div in listOfdiv:
        print('div = '+str(div))

def getAbstractDiv(listOfDivDict):
    flag=''
    befAbsDiv = []
    absDiv =[]
    aftAbsDiv = []
    for div in listOfDivDict:
        text = div.get('text').strip().lower()
        if flag == '':
            if 'abstract' in text:
                absDiv.append(div)
                flag = 'abstract'
            else:
                befAbsDiv.append(div)
            continue
        if flag == 'abstract':
            if 'introduction' in text:
                aftAbsDiv.append(div)
                flag = 'introduction'
            else:
                absDiv.append(div)
            continue
        if flag =='introduction':
            aftAbsDiv.append(div)
    # print('-----------before-----------')
    # printDiv(befAbsDiv)
    # print('----------abstract--------')
    # printDiv(absDiv)
    # print('------------after----------')
    # printDiv(aftAbsDiv)
    return befAbsDiv, absDiv, aftAbsDiv
    # return absText

def extractTextFromAbs(absDiv):
    abs=''
    for div in absDiv:
        # abs = abs + div['text']
        if abs.endswith('-'):
            abs = abs[:-1] + div['text']
        else:
            abs = abs+' ' +div['text']
    # print('abs = '+str(abs))
    return abs

def cleanPage(page):
    tempPage =[]
    for para in page:
        if len(para.strip())>=1:
            tempPage.append(para)
    # tempPage = page
    return tempPage

def combinePage(page01, page02):
    tempPage = page01[:-1]
    conPara = page01[-1]+' '+page02[0]
    tempPage.append(conPara)
    tempPage = tempPage + page02[1:]
    return cleanPage(tempPage)

def download_file(file_url, fileName):
    # outputfile = "document.pdf"
    # outputfile = fileName
    # response = urllib3.PoolManager().request('GET', file_url)
    # file = open(outputfile, 'wb')
    # file.write(response.data)
    # file.close()
    # print("Completed")
    # currDir = os.getcwd()
    wget.download(file_url, fileName)
    return fileName
    pass


def pdf2htmlEX(inputfilePath):
    # outputfile = "pdf2htmlEX_out"
    # outputfile = outputfile
    # -f start page   -l  end page
    # command = 'pdf2htmlEX --zoom 1.3 '+inputfile+' -f 3 -l 30 --dest-dir '+ outputfile
    print('url = '+str(inputfilePath))

    inputfileName = getFileName(inputfilePath).replace('-','_')
    # outputfile = download_file(inputfilePath, inputfileName)
    outputfile = 'InfoCom09_bc.pdf'
    print('out put file = '+str(outputfile))
    output_path=externalPath

    if not os.path.exists('/'+output_path+'/'+inputfileName.replace('.pdf','')):
        # os.chmod('/', 0o777)
        # os.makedirs('/'+inputfileName.replace('.pdf',''))
        # print('folder not exist')
        commandtemp = 'mkdir '+output_path+'/'+inputfileName.replace('.pdf','')
        subprocess.call(commandtemp, shell=True)

    command = 'pdf2htmlEX --zoom 1.3 --embed fi ' + inputfileName+ ' --dest-dir '+ output_path+'/'+inputfileName.replace('.pdf','')
    process = subprocess.call(command, shell=True)
    htmlFilePath = output_path+'/'+inputfileName.replace('.pdf','')+'/'+inputfileName.replace('.pdf','.html')
    print('html file path = '+str(htmlFilePath))
    return htmlFilePath

def getFileName(inputfilePath):
    return os.path.basename(inputfilePath)

def removeFold(inputfilePath):
    inputfileName = getFileName(inputfilePath)
    commandtemp = 'rm -r ' + output_path+'/'+inputfileName.replace('.pdf', '')
    subprocess.call(commandtemp, shell=True)
    pass



 # filter lines 短又没有顶格的， 很有可能是公式
def filterLine(listOfLine,lineDist, left, right):
    tempListOfLine =[]
    for line in listOfLine:
        text=getTextFromLine(line)
        if line[0].get('class').get('left') == left or line[0].get('class').get('left') == right:
            tempListOfLine.append(line)
        else:
            if len(text)>15 and len(line)<10:
                tempListOfLine.append(line)
    return tempListOfLine

def getTextFromPDF(filePath):
    listOfTotalLine = []
    # convert pdf to html

    startingTime00 = datetime.now()
    # htmlFilePath = pdf2htmlEX(filePath)
    htmlFilePath = filePath
    endingTime00 = datetime.now()

    print('time for convert pdf to html = '+ str(endingTime00-startingTime00))


    startTime = datetime.now()
    # get the css in html
    cssText = getCSStext(htmlFilePath)
    # parse css text to dictionary
    classDict = getValueOfClass(cssText)
    endingTime = datetime.now()
    print('time for parse css = ' + str(endingTime - startTime))

    # print('now = ', startTime.hour, ':', startTime.minute, ':', startTime.second, '.', startTime.microsecond)
    # print('endingTime = ', endingTime.hour, ':', endingTime.minute, ':', endingTime.second, '.', endingTime.microsecond)

    soup = getSoup(htmlFilePath)
    PAGEID = 1
    numOfPage = len(soup)

    firstPage = []
    listOfDivDict = getDivDictWithGivenClass(soup, PAGEID)

    befAbsDiv, absDiv, aftAbsDiv = getAbstractDiv(listOfDivDict)
    absText = extractTextFromAbs(absDiv)
    firstPage.append(absText)
    # listOfDivDict = aftAbsDiv

    left, right, fs = getLeftAndRight(aftAbsDiv, classDict)
    # print('left, right = ' + str(left) + '  ' + str(right))
    listOfLine = getListOfLine(absDiv, classDict, left, right)
    listOfTotalLine.extend(listOfLine)
    listOfLine = getListOfLine(aftAbsDiv, classDict, left, right)
    # mostFs 是行间距
    mostFs, lineDist = getMostFrequencyDist(listOfLine, classDict)
    # filter lines 短又没有顶格的， 很有可能是公式
    listOfLine= filterLine(listOfLine, lineDist,left, right)
    listOfTotalLine.extend(listOfLine)

    page = combinePara(listOfLine, classDict, left, right)

    Pages = firstPage + page
    Pages = cleanPage(Pages)
    # listOfpage.append(firstPage)


    for i in range(2, numOfPage + 1):
        # print('i = ' + str(i))
        listOfDivDict = getDivDictWithGivenClass(soup, i)
        left, right, fs = getLeftAndRight(listOfDivDict, classDict)
        # print('left, right = ' + str(left) + '  ' + str(right))
        listOfLine = getListOfLine(listOfDivDict, classDict, left, right)

        # mostFs 是行间距
        mostFs, lineDist = getMostFrequencyDist(listOfLine, classDict)
        # filter lines 短又没有顶格的， 很有可能是公式
        listOfLine= filterLine(listOfLine, lineDist,left, right)
        listOfTotalLine.extend(listOfLine)


        # for line in listOfLine:
        #     print('page id = ' + str(i))
        #     print('line = '+str(line))
        # getMostFrequencyDist(listOfLine,classDict)

        page = combinePara(listOfLine, classDict, left, right)
        # listOfpage.append(cleanPage(page))
        Pages = combinePage(cleanPage(Pages), cleanPage(page))

    outputfile = open('output/outputFile.txt', 'w')
    # for page in listOfpage:
    for pg in Pages:
        # print('paragraph = ' + pg)
        outputfile.write(pg+'\n')
        # print('page = '+str(pg)+" length = "+str(len(pg)))
        outputfile.write(' -------------\n')
    outputfile.close()

    # print('file path = '+ str(filePath))

    # removeFold(filePath)

    return Pages, listOfTotalLine

#   pagedict{"id":"sentDict"
#   }
# store sentence in dictionary

# sentDict{'id':{'text':sent
#                 'lines':[]  }
#
# }
#
def getSentDictFromPage(pages):
    pageDict={}
    sentDict={}
    i = 0
    for page in pages:
        sentList = segment_by_sentence(page, 'en')
        for sent in sentList:
            # print('sent = '+str(sent))
            sentDict['text'] = replaceSpecialUnicode(sent)
            # print('sent Dict = '+str(sentDict))
            pageDict[i]=deepcopy(sentDict)
            # pageDict['textDict'] = sentDict
            i = i+1
            pass
    return pageDict


if __name__ == '__main__':

    inputfilePath = 'https://www.aclweb.org/anthology/P15-1109.pdf'
    inputfilePath = 'https://arxiv.org/pdf/1310.5426.pdf'
    # inputfilePath = 'https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=5061914'
    # inputfilePath = "output/testPDFs/A_New_Financial_Policy_at_Swedish_Match_unlocked/A_New_Financial_Policy_at_Swedish_Match_unlocked.html"
    #
    inputfilePath = "testPDFs/InfoCom09_bc.pdf"
    # # pages 是一个list, 每一个item就是一个paragraph
    pages, listOfTotalLine = getTextFromPDF(inputfilePath)
    print('pages = '+str(pages))
    # # index sentence
    # pageDict = getSentDictFromPage(pages)
    # for key in pageDict:
    #     print(key, ' = ', pageDict[key]['text'])
    # # print(json.dumps(pageDict, indent=4))
    pass





