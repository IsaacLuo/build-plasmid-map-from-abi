import sys
import os
import json
import myabiparser


if len(sys.argv)<=1:
    print "no paramters"
    print "python abi2json.py 001.ab1"
else:
    name = sys.argv[1].split("_")[-1]
    try:
        a = myabiparser.open_trace2(sys.argv[1])
        a.setTraces()

        print json.dumps({"name":name,"sequence":a.sequence,"Q":a.Q,"AP":a.AP,"AV":a.AV,"CP":a.CP,"CV":a.CV,"GP":a.GP,"GV":a.GV,"TP":a.TP,"TV":a.TV,"result":"OK"})

    except:
        print json.dumps({"name":name,"result":"Can't read this file, file maybe corrupt or wrong format"})
