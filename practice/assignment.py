import re

if __name__ == '__main__':
    numOutputs = int(input(''))
    numInputs  = int(input(''))
    
    dictItems = 0
    tweetsDict = {}
    print ('enter {} tweets..'.format(numInputs))
    
    for i in range(0, numInputs):
        tweet = raw_input("")
        try:
            name, tweetId = re.search(r'^(\w+)\s+tweet_id_(\d+)', tweet, re.IGNORECASE).groups()
            if (tweetsDict.get(name)):
                tweetsDict[name] += 1
            else:
                dictItems += 1
                tweetsDict[name] = 1
        except:
            print ('entry #{} is in incorrect format!'.format(i))
            pass

    sorted_list = sorted(tweetsDict)
    l = len(sorted_list)
    i = 0
    j = 0

    while(i < numOutputs):
        n = int(tweetsDict[sorted_list[j]])
        print ('{} {}'.format(sorted_list[j], n))
        if (j+1 >= l):
            i +=1
        elif (n != int(tweetsDict[sorted_list[j+1]])):
            i +=1
        j += 1    


    
