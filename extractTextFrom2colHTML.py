#!/usr/bin/env python
# coding: utf-8
from datetime import datetime
from copy import deepcopy
from parser.htmlParser import getCSStext, getValueOfClass, getSoup, getClassName, hasAttX, getLongestWS, getBaseValue, printPages
from tool.tool import numItemInInterval
import math
import subprocess
import os
from extractTextFromHTML import getTextFromHTML

# get children text nodes from a node
def getTextNodes(node,classDict,totalPages, pageID=0,level=1, absX=0, absY=0):
    tempAbsX=absX
    tempAbsY=absY
    page=[]
    txtNodeDict={}
    if node.has_attr('data-page-no'):
        pageID = node['data-page-no']
    else:
        pageID = pageID
    # print('page id = ' + str(pageID))
    for subNode in node:
        absX=tempAbsX
        absY=tempAbsY
        if len(subNode['class']) == 11:
            txtNodeDict['text'] = subNode.getText()
            txtNodeDict['pageID'] = pageID
            txtNodeDict['totalPages'] = totalPages
            txtNodeDict['fs'] = classDict[getClassName(subNode['class'], 'fs')]
            x=classDict[getClassName(subNode['class'], 'x')]
            txtNodeDict['x'] = deepcopy(x)
            txtNodeDict['absX'] = deepcopy(absX)+deepcopy(x)
            y=classDict[getClassName(subNode['class'], 'y')]
            txtNodeDict['y'] = deepcopy(y)
            txtNodeDict['absY'] = absY +y
            txtNodeDict['level'] = level
            txtNodeDict['transform'] = getClassName(subNode['class'], 'm')
            # if 'x62' in subNode['class'] and 'y1b1' in subNode['class']:
            txtNodeDict['insertedWS'] = getLongestWS(subNode,classDict)
            page.append(deepcopy(txtNodeDict))
        else:
            if hasAttX(subNode,X='x'):
                absX=absX+classDict[getClassName(subNode['class'], 'x')]
            if hasAttX(subNode,X='y'):
                absY = absY + classDict[getClassName(subNode['class'], 'y')]
            level = level+1
            subpage=getTextNodes(subNode, classDict,totalPages,pageID,level,absX,absY)
            page.extend(subpage)

    return page

# remove noise text node,  text node with big difference for base font-size and contain long white space.
# filter reference
def shallowRemoval(pages):
    cleanPages=[]
    for page in pages:
        cleanPage = []
        for txtnode in page:
            if txtnode['text'].lower() == 'references':
                cleanPages.append(cleanPage)
                return cleanPages
            if txtnode['insertedWS'] > 50:
                pass
            elif abs(txtnode['fs']-txtnode['base_FS'])>4:
                pass
            else:
                cleanPage.append(txtnode)
        cleanPages.append(cleanPage)
    return cleanPages

# get the central line(median) of the page
def getMedianFromPage(page):
    median=0
    maxNum=0
    listX=[]
    for item in page:
        listX.append(item['absX'])
    listX.sort()
    # print('list X = '+str(listX))
    initMedian = math.floor((listX[-1]-listX[0])/3+listX[0])
    # print('inital median = '+str(initMedian))
    while initMedian<listX[-1]:
        temp=numItemInInterval(listX,initMedian,initMedian+5)
        if temp>maxNum:
            maxNum=temp
            median=initMedian
        initMedian=initMedian+5
    return median

# get the left and right peaks of the page. 计算分列的起点
def getTwoPeaks(pages):
    maxNum=0
    secondMaxNum =0
    peak1=0
    peak2 =0
    listX=[]
    for page in pages:
        for txtNode in page:
            # only consider the text node have more then 5 characters
            if len(txtNode['text'])>=5:
                listX.append(txtNode['absX'])
    listX.sort()

    initMedian = 0
    xCountList=[]
    while initMedian<listX[-1]:
        temp=numItemInInterval(listX,initMedian,initMedian+5)
        xCountList.append(deepcopy(temp))
        if temp<maxNum and temp>=secondMaxNum:
            secondMaxNum=temp
            peak2 = initMedian
        elif temp>=maxNum:
            secondMaxNum = maxNum
            maxNum = temp
            peak2 = peak1
            peak1 = initMedian
        else:
            pass
        initMedian=initMedian+5
    layout = getlayoutfromlist(xCountList)



    if peak1<peak2:
        return peak1, peak2, layout
    else:
        return peak2, peak1, layout

#sort node in page, page is a list of line, line is a list of txtNode
def sortLineInPage(page, median):
    newPage=[]
    if len(page)==0:
        return page
    # frontLine = page[0]
    length = len(page)
    for index in range(length):
        frontLine = page[index]
        for i in range(index+1, length):
            if compareLine(frontLine,page[i], median)==1:
                pass
            else:
                temp = page[i]
                page[i] = frontLine
                frontLine = temp
        newPage.append(frontLine)
    return newPage

def compareLine(rightLine, leftLine, median):
    result = 1
    # print('right line 0 = '+str(rightLine))
    if (rightLine[0]['absX']-median)*(leftLine[0]['absX']-median)>0:
        if rightLine[0]['absY']>leftLine[0]['absY']:
            return 1
        else:
            return -1
    else:
        if rightLine[0]['absX'] < leftLine[0]['absX']:
            return 1
        else:
            return -1
    return result

def insertNodeToNewPage(newPage,txtNode, median):
    dist= 10
    tempLine = []
    tempListOfLine = []
    flag = False
    for line in newPage:
        if abs(line[0]['absY'] - txtNode['absY'])<dist and (flag == False):
            # check if new node in the same side as line
            if (line[0]['absX']-median)*(txtNode['absX']-median)>0:
                # line = insertNodeToLine(line, txtNode)
                line.append(txtNode)
                flag = True
        tempListOfLine.append(line)

    if flag==False:
        tempLine.append(txtNode)
        tempListOfLine.append(tempLine)

    return tempListOfLine

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

# calculate most frequent font-size and lineSpace
#Page is a list of line, line is a list of txtNodeDict
def calFreFSandLineSpace(page):
    newPage=[]
    for line in page:
        line[0]['lineSpace'] = getMostFreValueOfKey(page, 'preSpace')
        line[0]['freqFS'] = getMostFreValueOfKey(page,'fs')
        line[0]['freqLevel'] = getMostFreValueOfKey(page, 'level')
        newPage.append(deepcopy(line))

    return newPage

# calculate the space between the txtNode and this txtNode's previous txtNode.
def calculatePreSpace(page):
    newPage = []
    lastBottom = 0
    lastIndex = len(page)-1
    for index,line in enumerate(page):
        # print('bottom = '+str(lastBottom))
        if index == 0 :
            preSpace = lastBottom
            lastBottom = line[0]['absY']
            line[0]['preSpace'] = preSpace
        else:
            # preSpace = abs(lastBottom - line[0]['absY'])
            preSpace = lastBottom - line[0]['absY']
            lastBottom=line[0]['absY']
            line[0]['preSpace']=preSpace
            if index != lastIndex:
                 newPage[index-1][0]['nextSpace'] = preSpace
            else:
                line[0]['nextSpace'] = 0

        newPage.append(deepcopy(line))
    return newPage

# calculate the space between the lines for pages.
def reCalculatePreSpace(pages):
    tempPages=[]
    for page in pages:
        tempPages.append(deepcopy(calculatePreSpace(page)))
    return tempPages



# get newPage, newPage is a list of line, line is a list of txtNode
def getNewPage(page, median):
    newPage=[]  # list of line
    # print('--------------mark--------------')
    for txtNode in page:
        # print('text node = '+str(txtNode))
        newPage = insertNodeToNewPage(newPage,txtNode, median)


    newPage = sortLineInPage(newPage, median)
    newPage = calculatePreSpace(newPage)
    newPage = calFreFSandLineSpace(newPage)
    # newPage = removeNoise(newPage)

    return newPage

def getTextFromLine(line):
    text = ''
    for node in line:
        text = text + node['text']
    # print('text in line = '+str(text))
    return text


# get the text node in each node
def getPages(soup,classDict):
    totalPages = len(soup)
    pages=[]
    for item in soup:
        page = getTextNodes(item,classDict,totalPages=totalPages,pageID=0,level=1, absX=0, absY=0)
        pages.append(deepcopy(page))
    for page in pages:
        for txtNode in page:
            txtNode['base_FS']= getBaseValue(pages, 'fs')
            txtNode['base_tf']=getBaseValue(pages,'transform')
    return pages


def getTxtFromNewPages(newPages):
    paras = []
    para=''
    for page in newPages:
        for index, line in enumerate(page):
            # print('line txt = '+getTextFromLine(line))
            if isNewPara(page,line):
                paras.append(deepcopy(para))
                para = getTextFromLine(line)
            else:
                para = combineParaAndLine(para, getTextFromLine(line))
    paras.append(deepcopy(para))
    return paras


def combineParaAndLine(para, txt):
    newPara = ''
    if para.endswith('-'):
        newPara = para[:-1]+txt
    else:
        newPara = para+' '+txt
    return newPara

def isNewPara(page, line):
    if len(page)<=1:
        return True


    index = page.index(line)
    if index==0 and line[0]['indent']>6:
        return True
    elif abs(line[0]['indent']-page[index-1][0]['indent'])<2 and abs(line[0]['preSpace']-line[0]['lineSpace'])<2:
        return False
    # elif line[0]['indent']>6 and getTextFromLine(line)[0].isupper():
    elif line[0]['indent']>6 and getTextFromLine(line)[0].isupper():
        return True
    elif abs(line[0]['preSpace']-line[0]['lineSpace'])>6 and (not getTextFromLine(line)[0].islower()):
        return True
    else:
        return False

def calculateIndent(newPages, lpeak, rpeak):
    tempPages = []
    for page in newPages:
        tempPage = []
        for index, line in enumerate(page):
            if line[0]['absX']-rpeak < -5:
                line[0]['indent'] = abs(line[0]['absX'] - lpeak)
            else:
                line[0]['indent'] = abs(line[0]['absX'] -rpeak)
            line[0]['nodeDensity'] = len(getTextFromLine(line))/len(line)
            tempPage.append(deepcopy(line))
        tempPages.append(deepcopy(tempPage))
        tempPage.clear()
    return tempPages

def isStartWithKeywords(str):
    list=['Fig.','Figure','Table']
    for item in list:
        if str.startswith(item):
            return True
    return False

def deepRemoval(newPages):
    tempPages = []
    for page in newPages:
        tempPage = []
        for index, line in enumerate(page):
            if line[0]['text'].lower().strip()=='references':
                tempPages.append(deepcopy(tempPage))
                return tempPages
            elif line[0]['indent']>50:
                pass
            # elif isStartWithKeywords(line[0]['text']):
            #     pass
            elif line[0]['nodeDensity']<3:
                pass
            # elif abs(line[0]['preSpace']-line[0]['lineSpace'])>6 and abs(line[0]['nextSpace']-line[0]['lineSpace'])>6 and getTextFromLine(line).strip()[-1].isalpha():
            #     pass
            else:
                tempPage.append(deepcopy(line))
        tempPages.append(deepcopy(tempPage))
        tempPage.clear()
    return tempPages

def getlayoutfromlist(xCountList):
    print('x count list = '+str(xCountList))
    xCountList.sort(reverse=True)
    if len(xCountList)<4:
        return 'single'
    total = sum(xCountList)
    # print("x count list 0 "+str(xCountList[0]))
    # print("x count list 1 " + str(xCountList[1]))
    # print('total = '+str(total))
    if (xCountList[0]/total)>0.28 and  (xCountList[1]/total)>0.28:
        return 'double'
    else:
        return 'single'


def getlayoutInfo(htmlFilePath):
    # startTime = datetime.now()
    newPages = []
    # get the css in html
    cssText = getCSStext(htmlFilePath)
    # parse css text to dictionary
    classDict = getValueOfClass(cssText)

    soup = getSoup(htmlFilePath)
    pages = getPages(soup, classDict)

    pages = shallowRemoval(pages)

    listX=[]
    for page in pages:
        for txtNode in page:
            # only consider the text node have more then 5 characters
            if len(txtNode['text'])>=5:
                listX.append(txtNode['absX'])
    listX.sort()

    # print('list of x = '+str(listX))

    initMedian = 0
    xCountList=[]
    while initMedian<listX[-1]:
        temp=numItemInInterval(listX,initMedian,initMedian+5)
        xCountList.append(deepcopy(temp))
        initMedian=initMedian+5
    # print('x count list = '+ str(xCountList))
    return xCountList


def getTextFrom2HTML(htmlFilePath, auto="auto"):
    # startTime = datetime.now()
    newPages = []
    # get the css in html
    cssText = getCSStext(htmlFilePath)
    # parse css text to dictionary
    classDict = getValueOfClass(cssText)

    soup = getSoup(htmlFilePath)
    pages = getPages(soup, classDict)


    # --------------------------------- shallow removal --------------------------------
    # remove noise text node,  text node with big difference for base font-size and contain long white space.
    # and remove reference
    pages = shallowRemoval(pages)
    # printPages(pages)
    # -------------------分列， get peaks,  create newPages----------------------------
    lpeak, rpeak, layout = getTwoPeaks(pages)
    layout = 'double'
    print('lpeak = '+ str(lpeak))
    print('rpeak = '+ str(rpeak))
    print('layout = '+str(layout))

    if abs(lpeak-rpeak)<20:
        layout='single'


    if auto=='single' or auto=='double':
        layout = auto
    else:
        layout = layout

    if layout == 'single':
        paras=[]
        text = getTextFromHTML(htmlFilePath)
        for key in text:
            paras.append(text[key])
        return paras


    # printPages(pages)
    for page in pages:
        newPage = getNewPage(page, rpeak)
        newPages.append(newPage)

    newPages = calculateIndent(newPages, lpeak, rpeak)


    # -------------------------- deep removal -----------------------------

    # printPages(newPages)
    newPages = deepRemoval(newPages)
    # printPages(newPages)

    # re-calculate the space between lines after remove some noise lines
    newPages = reCalculatePreSpace(newPages)

    print('------------\n')
    print('------------\n')

    newPages = deepRemoval(newPages)

    # printPages(newPages)

    # ---------------------------get text from newPages ---------------------
    paras = getTxtFromNewPages(newPages)

    return cleanParas(paras)

def cleanParas(paras):
    newParas=[]
    outputfile = open('output/outputFile.txt', 'w')
    for para in paras:
        para = para.replace('  ',' ')
        if len(para)<5:
            pass
        elif len(para)<60 and para.strip()[-1].isalpha():
            pass
        else:
            # print('para = ' + str(para))
            outputfile.write(str(para) + '\n')
            outputfile.write('---------------------\n')

            newParas.append(deepcopy(para))
    outputfile.close()
    return newParas

def writeParaToTxt(paras, outputFilePath):
    outputfile = open(outputFilePath, 'w')
    for para in paras:
        outputfile.write(str(para).replace('  ', ' ') + '\n')
        outputfile.write('---------------------\n')
    outputfile.close()


def pdftohtml_test(subpath):
	# for test
	filePath = subpath.replace(' ','_').replace('-','_')

	fileName = os.path.basename(filePath)
	print('file name = '+str(fileName))

	if not os.path.exists('/' + filePath.replace('.pdf', '')):
		commandtemp = 'mkdir ' + filePath.replace('.pdf', '')
		subprocess.call(commandtemp, shell=True)

	command = 'pdf2htmlEX --zoom 1.3 --embed fi ' + filePath + ' --dest-dir '  + filePath.replace(
		'.pdf', '')
	process = subprocess.call(command, shell=True)
	htmlFilePath = filePath.replace('.pdf', '')+"/"+fileName.replace('.pdf', '.html')
	print('html file path = ' + str(htmlFilePath))
	return htmlFilePath



if __name__ == '__main__':
    pass