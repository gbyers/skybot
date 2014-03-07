from base64 import b64encode
from util import hook, http
import sys

@hook.event('*')
def sasl(paraml, input=None, conn=None):
    if conn.conf.get('sasl'):
        if input.command == "CAP":
            if paraml[1] == "LS":
                conn.cmd("CAP REQ :multi-prefix sasl")
            elif paraml[1] == "ACK":
                conn.cmd("AUTHENTICATE PLAIN")
        elif input.command == "AUTHENTICATE":
            if paraml[0] == "+":
                stuff = conn.conf.get('user')+"\0"+conn.conf.get('user')+"\0"+conn.conf.get('sasl_pass')
                conn.cmd("AUTHENTICATE %s"%(b64encode(stuff)))
        elif input.command == "903":
            conn.cmd("CAP END")
        elif input.command == "904" or input.command == "905":
            conn.cmd("QUIT")
            print "SASL authentication failed - invalid user or sasl_pass."
            sys.exit(0)