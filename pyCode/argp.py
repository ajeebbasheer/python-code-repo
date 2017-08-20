import argparse 
parser= argparse.ArgumentParser()
parser.add_argument("hi")
args = parser.parse_args()
print(args.hi)
