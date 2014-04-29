#!/usr/bin/python
import sys, commands

if len(sys.argv) == 2:
    output = []
    data = commands.getoutput("yaourt -Ss %s"%(sys.argv[1])).split("\n")
    for line in data:
        l = line.replace("core/","<span style=\"color:red;\">core/</span>").replace("extra/","<span style=\"color:red;\">extra/</span>").replace("aur/","<span style=\"color:purple;\">aur/</span>").replace("community/","<span style=\"color:purple;\">community/</span>").replace("[","<span style=\"background-color:yellow;color:black;\">[").replace("]","</span>").replace("multilib/","<span style=\"color:purple;\">multilib/</span>")
        output.append(l)
    print "\n".join(output)
