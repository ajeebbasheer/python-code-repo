import re

if __name__ == '__main__':
    numOutputs = int(input(''))
    numInputs  = int(input(''))
    
    tweetsDict = {}
    print ('enter {} tweets..'.format(numInputs))
    
    for i in range(0, numInputs):
        tweet = raw_input("")
        try:
            name, tweetId = re.search(r'^(\w+)\s+tweet_id_(\d+)', tweet, re.IGNORECASE).groups()
            if (tweetsDict.get(name)):
                tweetsDict[name] += 1
            else:
                tweetsDict[name] = 1
        except:
            print ('entry #{} is in incorrect format!'.format(i))
            pass

    sorted_list = sorted(tweetsDict, key = lambda k,v: v, reverse=True)
    dictItems  = len(sorted_list) 
    print (sorted_list)

    print (tweetsDict)

    i = 0
    notDone = 1
    print (i, numOutputs)
    while(notDone):
        n = int(tweetsDict[sorted_list[i]])
        print (n)
        print ('{} {}'.format(sorted_list[i], n))
        if (n == int(tweetsDict[sorted_list[i+1]])):
            numOutputs +=1
        i += 1
        if (i >= numOutputs or numOutputs > dictItems):
            notDone = 0


    
