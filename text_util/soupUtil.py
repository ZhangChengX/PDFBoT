

import bs4
from bs4 import BeautifulSoup
from copy import deepcopy
from .util import replaceSpecialUnicode, convertIntToHex

# get selection string
def getSelectStr(divClasses, tag):
    selectStr=tag
    for item in divClasses[:-1]:
        selectStr=selectStr+'.'+str(item)
    return selectStr, divClasses[-1]


# get the list of navigable string in tag
# tagSoup is soup object
# locateIndex is a list, the length of the list is the depth,  数值代表在每一层的第几个
def getNavigableStringObject(tagSoup,locateIndex):
    # tagSoup= BeautifulSoup(tag,'html.parser')
    # tagSoup=tagSoup.select('div')[0]
    # print('tag soup = '+str(tagSoup))
    # print('locate index = '+str(locateIndex))
    tempNavStrObjects=[]
    locateIndex=locateIndex
    tempNavStrObject={}
    # print('tag soup = '+str(tagSoup))
    for index, content in enumerate(tagSoup.contents):
        # print('content = '+str(content))
        if type(content) is bs4.element.NavigableString:
            # print('this is navigableString')
            if str(content).replace(' ', '').replace('-','') == '':
                continue
            tempIndex=deepcopy(locateIndex)
            tempIndex.append(index)
            tempNavStrObject['text']=str(content)
            tempNavStrObject['locateIndex']=deepcopy(tempIndex)
            tempNavStrObjects.append(deepcopy(tempNavStrObject))
            tempNavStrObject.clear()

        elif type(content) is bs4.element.Tag:
            # print('this is tag')
            tempIndex = deepcopy(locateIndex)
            tempIndex.append(index)
            tempNavStrObjects.extend(deepcopy(getNavigableStringObject(content, deepcopy(tempIndex))))
    return tempNavStrObjects

# get locate index of the start content of the sentence
# locate index is a list and shows where the object is in the
def getStartLocateIndex(NavStrObjects, sentence):
    startIndex=[]
    # print('navgable string objects = '+str(NavStrObjects))
    for i, item in enumerate(NavStrObjects):
        navStr = NavStrObjects[i]['text']
        # print('navgable string = ' + str(navStr.replace(' ', '').replace('-','')))
        # print('sentence = '+str(sentence.replace(' ', '').replace('-','')))
        # if sentence.replace(' ', '').replace('-','').startswith(navStr.replace(' ', '').replace('-','')):
        if isEndOverlap(navStr.replace(' ', '').replace('-',''),sentence.replace(' ', '').replace('-','')):
            # print('-----------------i = '+str(i))
            startIndex=NavStrObjects[i]['locateIndex']
            break
            pass
        else:
            continue
    return startIndex

def getStartLocateIndexFromLine(line, soup, sentence):
    index=0
    startIndex=[]
    for i, div in enumerate(line):
        selectStr, pageId = getSelectStr(div, 'div')
        pageNo = convertIntToHex(pageId)
        # listOfNavStrObject = getNavigableStringObject(soup.find('div', {"data-page-no": pageNo}).select(selectStr)[0], [])
        listOfNavStrObject = getNavigableStringObject(soup[str(div)],[])
        # print('navgable string2222 = ' + str(listOfNavStrObject))
        # print('sentence = 22222' + str(sentence))
        startLocateIndex = getStartLocateIndex(listOfNavStrObject, sentence)

        # print('i div = '+str(i))
        # print('start locate index 111= '+str(startLocateIndex))
        if len(startLocateIndex)!=0:
            startIndex = startLocateIndex
            index = i
            break
    return index, startIndex

# get the ending content of the sentence
def getEndingLocateIndex(NavStrObjects, sentence):
    endingIndex = []
    for i, item in enumerate(NavStrObjects):
        navStr = NavStrObjects[i]['text']

        # if sentence.replace(' ', '').replace('-', '').endswith(navStr.replace(' ', '').replace('-', '')):
        # if isEndOverlapBackforward(sentence.replace(' ', '').replace('-', ''),navStr.replace(' ', '').replace('-', '')):
        if isEndOverlap(sentence.replace(' ', '').replace('-',''),navStr.replace(' ', '').replace('-', '')):
            endingIndex = NavStrObjects[i]['locateIndex']
    pass
    return endingIndex

def getEndingLocateIndexFromLine(line, soup, sentence):
    index=0
    endingIndex=[]
    # print('line == '+str(line))
    for i, div in enumerate(line):
        selectStr, pageId = getSelectStr(div, 'div')
        pageNo = convertIntToHex(pageId)
        # listOfNavStrObject = getNavigableStringObject(soup.find('div', {"data-page-no": pageNo}).select(selectStr)[0], [])
        listOfNavStrObject = getNavigableStringObject(soup[str(div)],[])
        # print('list of navigable str = '+str(listOfNavStrObject))
        endingLocateIndex = getEndingLocateIndex(listOfNavStrObject, sentence)
        # print('ending locate index == '+str(endingLocateIndex))
        if len(endingLocateIndex)!=0:
            endingIndex = endingLocateIndex
            index = i
            break
    return index, endingIndex


# colour the first div of the sentence
# startIndex is the start point of sentence
def getColouredFirstDivSoup(startIndex, tagStr, colourStr):
    souplocal=BeautifulSoup(tagStr,'html.parser').contents[0]
    # print('soup = '+str(souplocal))
    # print(type(souplocal))
    # print('start index = ' + str(startIndex))
    length = len(startIndex)


    if length==1:
        markup = "<" + str(souplocal.name) + "></" + str(souplocal.name) + ">"
        newSoup = BeautifulSoup(markup, 'html.parser').contents[0]
        # newSoup=deepcopy(souplocal.clear())
        try:
            newSoup['class'] = souplocal['class']
        except :
            print("**************tag has no attribute class******************")
            try:
                newSoup['color'] = souplocal['color']
            except:
                print("**************tag has no attribute color******************")

        # print('new soup '+str(newSoup))
        # print(type(newSoup))
        # colourId="background-color:lightblue"
        colourMarkup="<font class=\""+str(colourStr)+"\"></font>"
        # print('colour markup = '+str(colourMarkup))
        colourSoup=BeautifulSoup(colourMarkup,'html.parser').contents[0]

        for index, content in enumerate(souplocal.contents):
            if index<startIndex[0]:
                newSoup.append(deepcopy(content))
            elif index==startIndex[0]:
                if type(content) is bs4.element.NavigableString:
                    colourSoup.append(deepcopy(content))
                elif type(content) is bs4.element.Tag:
                    newSoup.append(deepcopy(content))
            else:
                colourSoup.append(deepcopy(content))
            pass
        newSoup.append(colourSoup)
        # print('new soup = ' + str(newSoup))
        return str(newSoup)
    else:
        temIndex= startIndex[1:]
        tempSoupStr= getColouredFirstDivSoup(temIndex,str(souplocal.contents[startIndex[0]]),colourStr)
        tempSoup = BeautifulSoup(tempSoupStr, 'html.parser').contents[0]
        # print('tempSoupStr = '+str(tempSoupStr))
        # print('souplocal = '+str(souplocal.contents[startIndex[0]]))
        souplocal.contents[startIndex[0]].replace_with(tempSoup)

        markup = "<" + str(souplocal.name) + "></" + str(souplocal.name) + ">"
        newSoup = BeautifulSoup(markup, 'html.parser').contents[0]
        # newSoup=deepcopy(souplocal.clear())
        try:
            newSoup['class'] = souplocal['class']
        except:
            print("**************tag has no attribute class******************")
            try:
                newSoup['color'] = souplocal['color']
            except:
                print("**************tag has no attribute color******************")

        # print('new soup '+str(newSoup))
        # print(type(newSoup))
        # colourId="background-color:lightblue"
        colourMarkup = "<font class=\"" + str(colourStr) + "\"></font>"
        # print('colour markup = ' + str(colourMarkup))
        colourSoup = BeautifulSoup(colourMarkup, 'html.parser').contents[0]

        for index, content in enumerate(souplocal.contents):
            if index < startIndex[0]:
                newSoup.append(deepcopy(content))
            elif index == startIndex[0]:
                if type(content) is bs4.element.NavigableString:
                    colourSoup.append(deepcopy(content))
                elif type(content) is bs4.element.Tag:
                    newSoup.append(deepcopy(content))
            else:
                colourSoup.append(deepcopy(content))
            pass
        newSoup.append(colourSoup)
        # print('new soup = ' + str(newSoup))
        return str(newSoup)


        pass


# colour the ending div of the sentence
# endingIndex is the start point of sentence
def getColouredEndingDivSoup(endingIndex, tagStr, colourStr):
    localSoup = BeautifulSoup(tagStr, 'html.parser').contents[0]
    length = len(endingIndex)
    if length == 1:
        markup = "<" + str(localSoup.name) + "></" + str(localSoup.name) + ">"
        newSoup = BeautifulSoup(markup, 'html.parser').contents[0]
        newSoup['class'] = localSoup['class']

        # colourStr = "background-color:lightblue"
        colourMarkup = "<font class=\"" + str(colourStr) + "\"></font>"
        colourSoup = BeautifulSoup(colourMarkup, 'html.parser').contents[0]

        for index, content in enumerate(localSoup.contents):
            if index<=endingIndex[0]:
                colourSoup.append(deepcopy(content))
            else:
                newSoup.append(deepcopy(content))
        # newSoup.append(colourSoup)
        newSoup.insert(0,colourSoup)
        # print('new soup = ' + str(newSoup))
        return str(newSoup)
    else:
        temIndex = endingIndex[1:]
        tempSoupStr = getColouredEndingDivSoup(temIndex, str(localSoup.contents[endingIndex[0]]), colourStr)
        tempSoup = BeautifulSoup(tempSoupStr, 'html.parser').contents[0]
        # print('tempSoupStr = '+str(tempSoupStr))
        # print('souplocal = '+str(souplocal.contents[startIndex[0]]))
        localSoup.contents[endingIndex[0]].replace_with(tempSoup)
        # print('local soup iter = '+str(localSoup))

        markup = "<" + str(localSoup.name) + "></" + str(localSoup.name) + ">"
        newSoup = BeautifulSoup(markup, 'html.parser').contents[0]
        # newSoup=deepcopy(souplocal.clear())
        try:
            newSoup['class'] = localSoup['class']
        except:
            print("**************tag has no attribute class******************")
            try:
                newSoup['color'] = localSoup['color']
            except:
                print("**************tag has no attribute color******************")

        # print('new soup '+str(newSoup))
        # print(type(newSoup))
        # colourId="background-color:lightblue"
        colourMarkup = "<font class=\"" + str(colourStr) + "\"></font>"
        # print('colour markup = ' + str(colourMarkup))
        colourSoup = BeautifulSoup(colourMarkup, 'html.parser').contents[0]

        # print('ending index [0]= '+str(endingIndex))
        for index, content in enumerate(localSoup.contents):
            if index < endingIndex[0]:
                colourSoup.append(deepcopy(content))
            else:
                newSoup.append(deepcopy(content))
        # newSoup.append(colourSoup)
        # print('colour soup test = '+str(colourSoup))
        newSoup.insert(0, colourSoup)
        # print('new soup = ' + str(newSoup))
        return str(newSoup)

        pass

#     colour the whole div of in the middle of the sentence
def getColourdDivSoup(tagStr, colourStr):
    localSoup = BeautifulSoup(tagStr, 'html.parser').contents[0]

    markup = "<" + str(localSoup.name) + "></" + str(localSoup.name) + ">"
    newSoup = BeautifulSoup(markup, 'html.parser').contents[0]
    newSoup['class'] = localSoup['class']

    # colourStr = "background-color:lightblue"
    colourMarkup = "<font class=\"" + str(colourStr) + "\"></font>"
    colourSoup = BeautifulSoup(colourMarkup, 'html.parser').contents[0]

    for index, content in enumerate(localSoup.contents):
        colourSoup.append(deepcopy(content))

    newSoup.insert(0, colourSoup)
    return str(newSoup)
def ColourDivInSoup(soup,divClasses, colourStr):
    selectStr, pageId = getSelectStr(divClasses, 'div')
    pageNo= convertIntToHex(pageId)

    # tagStr=str(soup.find('div', {"data-page-no":pageNo}).select(selectStr)[0])
    tagStr = str(soup[str(divClasses)])
    localSoup = BeautifulSoup(tagStr, 'html.parser').contents[0]

    markup = "<" + str(localSoup.name) + "></" + str(localSoup.name) + ">"
    newSoup = BeautifulSoup(markup, 'html.parser').contents[0]
    newSoup['class'] = localSoup['class']

    # colourStr = "background-color:lightblue"
    colourMarkup = "<font class=\"" + str(colourStr) + "\"></font>"
    colourSoup = BeautifulSoup(colourMarkup, 'html.parser').contents[0]

    for index, content in enumerate(localSoup.contents):
        colourSoup.append(deepcopy(content))

    newSoup.insert(0, colourSoup)
    # soup.select(selectStr)[0].replace_with(newSoup)
    # soup.find('div', {"data-page-no": pageNo}).select(selectStr)[0].replace_with(newSoup)
    soup[str(divClasses)].replace_with(newSoup)
    # soup[str(divClasses)]=soup[str(divClasses)].replace_with(newSoup)
    soup[str(divClasses)]=newSoup


# Check if string ends with the beginning of another string
def isEndOverlap(str1, str2):
    for i in range(0, len(str1)):
        # print('str1 = '+str(str1))
        # print('str2 = ' + str(str2))
        if str2.startswith(str1[-i:]):
            # print('i = '+str(i))
            if i == 0:
                return True
            else:
                return i
    return 0

# Check if string ends with the beginning of another string
def isEndOverlapBackforward(str1, str2):
    for i in range(0, len(str2)):
        # print('str1 = '+str(str1))
        # print('str2 = ' + str(str2))
        if str1.endswith(str2[:-i]):
            # print('i = '+str(i))
            if i == 0:
                return True
            else:
                return i
    return 0

# # Check if string ends with the beginning of another string
# def isBeginningOverlap(str1, str2):
#     for i in range(0, len(str1)):
#         if str2.startswith(str1[-i:]):
#             return i
#     return 0



def getColourStr(colourId):
    if colourId == 0:
        colourStr = "colour00"
    elif colourId == 1:
        colourStr = "colour01"
    elif colourId == 2:
        colourStr = "colour02"
    elif colourId == 3:
        colourStr = "colour03"
    elif colourId == 4:
        colourStr = "colour04"
    elif colourId == 5:
        colourStr = "colour05"
    elif colourId == 6:
        colourStr = "colour06"
    elif colourId == 7:
        colourStr = "colour07"
    elif colourId == 8:
        colourStr = "colour08"
    elif colourId == 9:
        colourStr = "colour09"
    else:
        colourStr = "colour10"
    return colourStr







