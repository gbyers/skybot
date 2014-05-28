# -- coding: utf8 --
from util import hook
import sys, re, commands, math, cmath, random, time, subprocess

@hook.command
def python(inp, input=None):
    if input.nick.lower() in ["cups","nathan","jacob1"]:
        return pysandbox(inp)

def pysandbox(msg=None):
    if not msg: sys.exit("No Code")
    else:
        if ".__" in msg: return "Nope"
        if "['__" in msg and "__']" in msg or "[\"__" in msg and "__\"]" in msg: return "Nope"
        output = "import math, cmath, random;"
        output+= "safe_list = {};"
        output+= """safe_list["False"]=False;safe_list["True"]=True;safe_list["abs"]=abs;safe_list["divmod"]=divmod;safe_list["staticmethod"]=staticmethod;safe_list["all"]=all;safe_list["enumerate"]=enumerate;safe_list["int"]=int;safe_list["ord"]=ord;safe_list["str"]=str;safe_list["any"]=any;safe_list["isinstance"]=isinstance;safe_list["pow"]=pow;safe_list["sum"]=sum;safe_list["basestring"]=basestring;safe_list["issubclass"]=issubclass;safe_list["super"]=super;safe_list["bin"]=bin;safe_list["iter"]=iter;safe_list["property"]=property;safe_list["tuple"]=tuple;safe_list["bool"]=bool;safe_list["filter"]=filter;safe_list["len"]=len;safe_list["range"]=range;safe_list["type"]=type;safe_list["bytearray"]=bytearray;safe_list["float"]=float;safe_list["list"]=list;safe_list["unichr"]=unichr;safe_list["callable"]=callable;safe_list["format"]=format;safe_list["locals"]=locals;safe_list["reduce"]=reduce;safe_list["unicode"]=unicode;safe_list["chr"]=chr;safe_list["frozenset"]=frozenset;safe_list["long"]=long;safe_list["vars"]=vars;safe_list["classmethod"]=classmethod;safe_list["getattr"]=getattr;safe_list["map"]=map;safe_list["repr"]=repr;safe_list["xrange"]=xrange;safe_list["cmp"]=cmp;safe_list["globals"]=globals;safe_list["max"]=max;safe_list["reversed"]=reversed;safe_list["zip"]=zip;safe_list["compile"]=compile;safe_list["hasattr"]=hasattr;safe_list["memoryview"]=memoryview;safe_list["round"]=round;safe_list["complex"]=complex;safe_list["hash"]=hash;safe_list["min"]=min;safe_list["set"]=set;safe_list["apply"]=apply;safe_list["delattr"]=delattr;safe_list["help"]=help;safe_list["next"]=next;safe_list["setattr"]=setattr;safe_list["buffer"]=buffer;safe_list["dict"]=dict;safe_list["hex"]=hex;safe_list["object"]=object;safe_list["slice"]=slice;safe_list["coerce"]=coerce;safe_list["dir"]=dir;safe_list["id"]=id;safe_list["oct"]=oct;safe_list["sorted"]=sorted;safe_list["intern"]=intern;"""
        output+= "execdict = {'__builtins__': safe_list,'math': math,'cmath': cmath,'random': random};"
        output+= '\ntry:\n\texec(\"\"\"'+msg.replace("\"","'")+'\"\"\",execdict);\n'
        output+= "except BaseException, e:\n\tprint e;"
        #output+= "exec('"+msg+"',execdict);"
        f=open("sandbox.py","w+")
        f.write(output)
        f.close()
        output = commands.getoutput("python2 sandbox.py;rm sandbox.py")
        return output
