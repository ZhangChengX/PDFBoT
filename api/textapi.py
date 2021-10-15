import requests
import json



def getSentRank(text):
    apiUrl = 'http://dooyeed.com/api/sentences'
    # data to be sent to api
    dataDict = {'ratio': 1,
            'lang': 'en',
            'algorithm': 'semantic',
            'article_structure': '1',
            'text': text}


    # data = json.dumps(dataDict, indent=4)
    # print(data)
    # sending post request and saving response as response object
    res = requests.get(url=apiUrl, data=dataDict)
    print("response = "+str(res.json()['sentences']))
    with open('sentRankTemp.txt', 'w') as outfile:
        json.dump(res.json()['sentences'], outfile)

    return str(res.json()['sentences'])




if __name__ == '__main__':
    f =open("../readme.txt", "r")
    text = f.read()
    print('text = '+str(text))
    getSentRank(text)