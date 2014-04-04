# -- coding: utf-8 --
from util import hook, http
import re, HTMLParser, urllib, time

@hook.command("wp")
@hook.command
def wordpress(inp, say=None):
    "wordpress/wp <name> -- checks if the WordPress exists"
    domain = inp.split(" ")[0]
    url = "http://en.wordpress.com/typo/?"+urllib.urlencode({"subdomain":domain})
    try:
        data = http.get(url)
    except http.HTTPError, e:
        return (str(e))
    if "exist" in data:
        return "http://%s.wordpress.com/ doesn't exist"%domain
    else:
        return "http://%s.wordpress.com/ exists"%domain

def _search(inp, say):
    url = "http://duckduckgo.com/lite?"+urllib.urlencode({"q":inp.encode('utf8', 'ignore')})
    try:
        data = http.get(url)
    except http.HTTPError, e:
        say(str(e)+": "+url)
        return
    data = re.sub("\s+"," ", data)
    search = re.search("""<td valign="top">1.&nbsp;<\/td> <td> <a rel="nofollow" href="(.*?)" class='result-link'>(.*?)<\/a> <\/td> <\/tr> <tr> <td>&nbsp;&nbsp;&nbsp;<\/td> <td class='result-snippet'>(.*?)<\/td> <\/tr> <tr> <td>&nbsp;&nbsp;&nbsp;<\/td> <td> <span class='link-text'>(.*?)<\/span> <\/td> <\/tr>""",data)
    if search:
        resultdesc = re.sub('<[^<]+?>', '', search.group(3)[0:180].decode('utf8', 'ignore').strip()+"...")
        resulturl  = "\00312"+HTMLParser.HTMLParser().unescape(search.group(1))+"\003"
        resultdesc = HTMLParser.HTMLParser().unescape(resultdesc)
        say(resultdesc+" - "+resulturl)
    else:
        say("No results found.")

@hook.command
def tld(inp):
    "tld <tdl> -- returns info about the tld"
    if inp.startswith("."): _tld = inp[1:]
    else: _tld = inp
    if "." in _tld: _tld = _tld.split(".")[-1]
    try:
        data = http.get("http://www.iana.org/domains/root/db/%s.html"%_tld.encode("utf8","ignore"))
    except http.HTTPError, e:
        if "404:" in str(e):
            try:
                data = http.get("https://en.wikipedia.org/wiki/.%s"%_tld.encode("utf8","ignore"))
            except http.HTTPError, e:
                return "No match for %s"%_tld
            search = re.search("""<th scope="row" style="text-align:left;">Sponsor<\/th>\n<td><a href="(.*)" title="(.*)">(.*)<\/a><\/td>""",data)
            if search:
                return "TLD: %s - Sponsor: %s"%(_tld,search.group(3))
            else:
                return "No match for %s"%_tld
        else:
            return "No match for %s"%_tld
    search = re.search("""<b>(.*)<\/b><br\/>""",data)
    if search:
        sponsor = re.sub('<[^<]+?>', ' ', search.group(1))
        return "TLD: %s - Sponsor: %s"%(_tld.encode("utf8","ignore"),sponsor)

@hook.command
def translate(inp, say=None):
    "translate [[:from] :to] <text> -- translates text from one language to another. Defaults to from: auto, to: en"
    if inp.split(" ")[0].startswith(":") and inp.split(" ")[1].startswith(":"):
        t = inp.split(" ")[1][1:]
        f = inp.split(" ")[0][1:]
        m = inp.split(" ",2)[2].encode("utf8","ignore")
    else:
        t = "en"
        f = "auto"
        m = inp.encode("utf8","ignore")
    url = "http://translate.google.com/translate_a/t?"+urllib.urlencode({"client":"p","ie":"UTF-8","oe":"UTF-8","sl":f,"tl":t,"q":m})
    try:
        data = http.get_json(url.encode("utf8","ignore"))
    except http.HTTPError, e:
        return (str(e))
    words = []
    #return data
    if "sentences" in data:
        return data["sentences"][0]["trans"]
    elif "dict" not in data and "sentences" in data:
        return m
    else:
        for res in data["dict"][0]["entry"]:
            if "score" in res:
                words.append("%s (%s%% match)"%(res["word"],round(res["score"],4)*100))
            else:
                words.append(res["word"])
        return (", ".join(words))
        #return data["dict"][0]["entry"][0]["word"]+" "+data["dict"][0]["entry"][0]["reverse_translation"][0]
    
@hook.command
def rlysx(inp, say=None):
    "rlysx <url> -- converts long URL to a really sexy URL"
    try:
        data = (http.get("http://rly.sx/index.php?",post_data="shorten=true&"+urllib.urlencode({"url":inp})))
        if "rly.sx" in data: return "http://"+data
        else: return data
    except http.URLError, e:
        return e

@hook.command
def expand(inp, say=None):
    "expand <url> -- expands short URLs"
    try:
        return (http.open(inp).url.strip())
    except http.URLError, e:
        return ("Unable to expand")

#@hook.command("0click")
#@hook.command
@hook.regex("(.*)>\$(.*)")
def zeroclick(inp, say=None, input=None):
    "zeroclick/0click <search> -- gets zero-click info from DuckDuckGo"
    if input.nick.lower() not in ["ovd|relay","nebulae"]:
        url = "http://duckduckgo.com/lite?"
        params = {"q":inp.group(2).replace("\001","").encode('utf8', 'ignore')}
        url = "http://duckduckgo.com/lite/?"+urllib.urlencode(params)
        try:
            data = http.get(url)
        except http.HTTPError, e:
            say(str(e)+": "+url)
            return
        search = re.findall("""\t<td>.\t\s+(.*?).<\/td>""",data,re.M|re.DOTALL)
        if search:
            answer = HTMLParser.HTMLParser().unescape(search[-1].replace("<br>"," ").replace("<code>","\002").replace("</code>","\002"))
            answer = re.sub("<[^<]+?>","",answer)
            out = re.sub("\s+"," ",answer.strip())
            if out: return out.decode("utf8","ignore").split(" More at")[0]
            else: return ("No results")
        else:
            return ("No results found.")

@hook.command
def ddg(inp, say=None):
    "ddg <search> -- search DuckDuckGo"
    _search(inp, say)

@hook.command("r")
@hook.command
def reddit(inp, say=None):
    "reddit/r <search> -- search reddit"
    _search(inp+" site:reddit.com", say)

@hook.command
def imdb(inp, say=None):
    "imdb <search> -- search IMDB"
    _search(inp+" site:imdb.com", say)

@hook.command("gp")
@hook.command
def googleplay(inp, say=None):
    "googleplay/gp <search> -- search Google Play"
    _search(inp+" site:play.google.com", say)

#@hook.command("yt")
#@hook.command
#def youtube(inp, say=None):
#    "youtube/yt <search> -- search YouTube"
#    _search(inp+" site:youtube.com", say)

@hook.command("wiki")
@hook.command
def wikipedia(inp, say=None):
    "wikipedia/wiki <search> -- search Wikipedia"
    _search(inp+" site:wikipedia.org", say)

@hook.command(autohelp=False)
def pomf(inp, say=None):
    "pomf <search> -- search pomf.se"
    if inp:
        url = "http://moe.pomf.se/includes/api.php?"+urllib.urlencode({"do":"search","q":inp})
    try:
        data = http.get(url)
    except http.HTTPError, e:
        say(str(e)+": "+url)
        return
    if data:
        string = data.split("<br/>")
        del string[(-1)]
        out = ""
        for o in string:
            out += o.split(" - ")[0]+" - \00312http://a.pomf.se/"+o.split(" - ")[1].replace(" ","%20")+"\003 "
        say(out)
    else:
        say("No results")
    
@hook.command
def img(inp, say=None):
    "img <search> -- search Google Images"
    url = "http://www.google.com/search?"+urllib.urlencode({"q":inp,"tbm":"isch"})
    try:
        data = http.get(url)
    except http.HTTPError, e:
        say(str(e)+": "+url)
        return
    search = re.search('<a href="http://www.google.com/imgres?(.*?)imgurl=(.*?)&(.*?)"',data)
    if search:
        return (search.group(2).encode("utf8","ignore"))
    else:
        say("No results found.")
    print data

@hook.command
def suggest(inp, input=None, conn=None, say=None):
    url = "http://google.com/complete/search?"+urllib.urlencode({"q":inp,"output":"xml"})
    data = http.get(url)
    if data:
        suggestions = re.findall("""<suggestion data="(.*?)"\/>""",data)
        if suggestions:
            n=1
            l=[]
            for sug in suggestions:
                sug = HTMLParser.HTMLParser().unescape(sug).replace(inp,"\002%s\002"%inp)
                if n <= 5:
                    say("%s. %s"%(n,sug))
                    #time.sleep(0.75)
                    n=n+1
                else:
                    break
    else:
        return "No suggestions for %s"%inp

@hook.command
def whois(inp, input=None, conn=None, say=None):
    "whois <domain> -- get whois information for the domain."
    url = inp
    url = re.sub("https?:\/\/","",url)
    if "/" in url: url = url.split("/")[0]
    page = http.get("http://hostcabi.net/domain/%s"%url)
    if page:
        data = re.findall("<b>(IP Owner|Server Location|Description|Domain IP|Website Load Speed|Alexa Rank|Website Value|Website Daily Visitors|Website Daily Income):<\/b>(.*?)<td>(.*?)<\/td>",page)
        if data:
            out = []
            for item in data:
                stuff = re.sub("<[^<]+?>","",HTMLParser.HTMLParser().unescape(item[2])).rstrip()
                out.append(item[0]+": \002"+stuff+"\002")
            say("; ".join(out))
        else:
            return "Unable to lookup %s"%url
    else:
        return "Unable to lookup %s"%url

@hook.command
def torrent(inp, input=None, conn=None, say=None):
    "torrent <search> -- search TPB for torrents"
    s = inp.replace(" ","%20")
    page = http.get("http://thepiratebay.se/search/%s"%s)
    if page:
        data = re.search("""<a href="/torrent/(\d+)/(.*?)" class="detLink" title="(.*?)">(.*?)<\/a>""",page)
        if data:
            d = re.search("""<font class="detDesc">(.*?), ULed by""",page)
            sl = re.findall("""\t\t<td align="right">(\d+)<\/td>\n\t\t<td align="right">(\d+)<\/td>""",page)
            out = "%s (%s, \00309S\003: %s, \00304L\003: %s) - \002http://thepiratebay.se/torrent/%s\002"%(data.group(3),HTMLParser.HTMLParser().unescape(d.group(1)),sl[0][0],sl[0][1],data.group(1))
            say(out)   
        else:
            say("No torrents found")
    else:
        say("Unable to load page")

