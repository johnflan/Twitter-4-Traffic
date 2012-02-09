import sys

f = open(sys.argv[1], "r")
text = f.read()
text = text.replace("\t","    ")
f.close()

f = open(sys.argv[1], "w")
f.write(text)
f.close()
