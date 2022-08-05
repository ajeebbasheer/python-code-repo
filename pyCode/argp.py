import argparse
from ast import arguments
from turtle import position

TEST_ARGS = 'mydoc.txt -H ExitHandler -t tag1 tag2 -k error exception warn'
TEST_ARGS2 = 'mydoc.txt -k error exception warn debug log'

def parseArgs(arg_list=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help = "log file") # positional args
    parser.add_argument("-H", "--handler" , help = "log file") # optional args
    parser.add_argument("-t", "--tag", help = "tags to search", nargs=2)
    parser.add_argument("-k", "--keyword", help = "keywords to search",
                        nargs='*')
    return parser.parse_args(arg_list.split())

if __name__ == '__main__':
    args = parseArgs(TEST_ARGS)
    print(args.file)
    print(args.handler)
    print(args.tag)
    print(args.keyword)
    args = parseArgs(TEST_ARGS2)
    print(args.keyword)
