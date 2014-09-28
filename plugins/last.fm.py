# -- coding: utf8 --
from util import hook, http
import time, re

api_url = "http://ws.audioscrobbler.com/2.0/?format=json"

@hook.api_key('lastfm')
@hook.command('lfmc')
@hook.command(autohelp=False)
def lastfmcompare(inp, nick='', say=None, api_key=None):
    "lastfmcompare/lfmc <user1> <user2> -- compare 2 users to get a match"
    if inp.count(" ") == 1:
        user1 = inp.split(" ")[0]
        user2 = inp.split(" ")[1]
    response = http.get_json(api_url, method="tasteometer.compare", api_key=api_key, value1=user1, value2=user2, type1="user", type2="user", limit="15")

    if 'error' in response:
            return "error: %s" % response["message"]

    if "@attr" in response["comparison"]["result"]["artists"]:
        score = int(float(response["comparison"]["result"]["score"][0:4])*100)
        score = round(float(response["comparison"]["result"]["score"])*100,2)
        match = response["comparison"]["result"]["artists"]["@attr"]["matches"]
        say("\x02%s\x02 and \x02%s\x02 have a \x02%s%%\x02 match on last.fm"%(user1,user2,score))
    else:
        say("\x02%s\x02 and \x02%s\x02 do not have a match."%(user1,user2))

def formatTime(time):
    time = int(time)
    y=(time/60/60/24/365)
    d=(time/60/60/24%365)
    h=(time/60/60%60)
    m=(time/60%60)
    s=(time%60)
    out = ""
    if y == 1 and not out: out = "%s year ago"%y
    elif y > 1 and not out: out = "%s years ago"%y
    if d == 1 and not out: out = "%s day ago"%d
    elif d > 1 and not out: out = "%s days ago"%d
    if h == 1 and not out: out = "%s hour ago"%h
    elif h > 1 and not out: out = "%s hours ago"%h
    if m == 1 and not out: out = "%s min ago"%m
    elif m > 1 and not out: out = "%s mins ago"%m
    if s == 1 and not out: out = "%s sec ago"%s
    elif s > 1 and not out: out = "%s secs ago"%s
    return out

@hook.api_key('lastfm')
@hook.command('np', autohelp=False)
@hook.command('lfm', autohelp=False)
@hook.command(autohelp=False)
def lastfm(inp, nick='', say=None, api_key=None, db=None):
    "lastfm/np/lfm <user> -- gest current track or last played for <user>, also saves <user> to current nick"
    db.execute("create table if not exists lastfm(nick primary key, user)")
    if not inp:
        loc = db.execute("select user from lastfm where nick=lower(?)", (nick,)).fetchone()
        if loc:
            user = loc[0]
        else:
            return "Enter a username"
    else:
        user = inp
        db.execute("insert or replace into lastfm(nick, user) values (?,?)", (nick.lower(), inp))
        db.commit()

    response = http.get_json(api_url, method="user.getrecenttracks", api_key=api_key, user=user, limit=1)

    if 'error' in response:
        if inp:
            return "error: %s" % response["message"]
        else:
            return "your nick is not a Last.fm account. try 'lastfm <username>'."

    if not "track" in response["recenttracks"] or len(response["recenttracks"]["track"]) == 0:
        return "no recent tracks for user \x02%s\x0F found" % user

    api_json = response["recenttracks"]
    tracks = api_json["track"]
    last = None
    if type(tracks) == list:
        track = tracks[0]
        status = 0
    elif type(tracks) == dict:
        track = tracks
        last = int(tracks["date"]["uts"])
        status = 1

    title = track["name"]
    album = track["album"]["#text"]
    artist = track["artist"]["#text"]
    url = track["url"].replace("www.","").encode("utf8","ignore")
    #url = urllib2.unquote(urllib2.quote(url.encode("utf8"))).decode("utf8")
    url = urldecode(url).decode("utf8","ignore")
    if last:
        last = formatTime(int(time.time() - last))

    if status == 0:
        output = u"\x02%s\x0F is listening to \x02%s\x0F - \x02%s\x0F - %s" % (user,artist,title,url)
    elif status == 1:
        output = u"\x02%s\x0F was listening to: \x02%s\x0F - \x02%s\x0F ⌛ \x02%s\x0F - %s" % (user,artist,title,last,url)

    say(output)

def htc(m):
    return chr(int(m.group(1),16))

def urldecode(url):
    rex=re.compile('%([0-9a-hA-H][0-9a-hA-H])',re.M)
    return rex.sub(htc,url)
