from util import hook, http
import re, urllib, requests, time

def getnextday():
    if time.strftime('%w') == "0": return "Sunday"
    elif time.strftime('%w') == "1": return "Monday"
    elif time.strftime('%w') == "2": return "Tuesday"
    elif time.strftime('%w') == "3": return "Wednesday"
    elif time.strftime('%w') == "4": return "Thursday"
    elif time.strftime('%w') == "5": return "Friday"
    elif time.strftime('%w') == "6": return "Saturday"
    else: return 0

def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def stripspaces(data):
    p = re.compile(r"\s\s+")
    return p.sub('', data)

def getWeather(loc,nick):
    curdegc  = "0"
    curdegf  = "0"
    curwindm = "0"
    curwindk = "0"
    curwindd = "n/a"
    curhumid = "0"
    curcond  = "n/a"
    try:
        data = stripspaces(http.get("http://i.wund.com/cgi-bin/findweather/getForecast?"+urllib.urlencode({"brand":"iphone","query":loc.encode("utf8","ignore")})))
    except http.HTTPError, e:
        say(str(e)+": http://i.wund.com/cgi-bin/findweather/getForecast?"+urllib.urlencode({"brand":"iphone","query":loc}))
        return
    #data     = stripspaces(f.read())# .replace("\n","").replace("\r","").replace("\t","")
    location = """<h2>(.*?)</h2>"""
    location = re.search(location,data,re.M|re.I)
    if location: location = location.group(1)
    temperature = """<span class="nowrap"><b>(.*?)</b>&deg;(.*?)</span>"""
    temperature = re.findall(temperature,data,re.M|re.I)
    wind = """<span class="nowrap"><b>(.*?)</b>&nbsp;(.*?)</span>"""
    wind = re.findall(wind,data,re.M|re.I)
    winddir = re.search("<b>(.*?)</b> at",data,re.M|re.I)
    if temperature:
        curdegc = temperature[1][0]
        curdegf = temperature[0][0]
    if wind:
        curwindm = wind[0][0]
        curwindk = wind[1][0]
    if winddir:
        curwindd = winddir.group(1)
    humid = re.search("""<td><span class="b">(.*?)%</span></td>""",data,re.M|re.I)
    if humid:
        curhumid = humid.group(1)
    cond = re.search("<div>(.*?)</div>",data,re.M|re.I)
    kelvin = int(float(curdegc)*274.15)
    knots = int(float(curwindm)*0.868976241901)
    if cond:
        curcond = cond.group(1)
        curdeg = float(curdegc)
        if curdeg <= 0: curdeg = "darn cold out"
        elif curdeg >= 1 and curdeg <= 10: curdeg = "chilly out"
        elif curdeg >= 11 and curdeg <= 17: curdeg = "temperate"
        else: curdeg = "positively balmy"
        curwind = float(curwindm)
        if curwind >= 0 and curwind <= 3: wind = "not windy"
        elif curwind >= 4 and curwind <= 20: wind = "somewhat breezy"
        elif curwind >= 20 and curwind <= 27: wind = "very windy"
        else: wind = "your computer just blew away"
        if nick.lower() not in []:
             output = "%s: Currently %sF / %sC, humidity: %s%%, wind: %s at %smph / %skm/h, conditions: %s."%(location,curdegf,curdegc,curhumid,curwindd,curwindm,curwindk,curcond)
        else:
            output = "%s: Currently %s, humidity: %s%%, wind: %s, conditions: %s"%(location,curdeg,curhumid,wind,curcond)
        t = getnextday()
        forecast = re.search("""<span class="b">%s(.*?)<\/span><br \/><div>(.*?)<\/div>"""%t,data,re.M|re.I)
        if forecast:
            output += " Forecast: "+forecast.group(2)
        return output
    else:
        return "Location not found."

@hook.command('w',autohelp=False)
@hook.command(autohelp=False)
def weather(paraml, nick='', db=None):
    "weather <location> -- gets weather data from Wunderground"
    loc = paraml.encode("utf8","ignore").decode("utf8","ignore")
    db.execute("create table if not exists weather(nick primary key, loc)")
    if not paraml:
        loc = db.execute("select loc from weather where nick=lower(?)", (nick,)).fetchone()
        if not loc:
            return weather.__doc__
        loc = loc[0]
    else:
        loc = paraml
        db.execute("insert or replace into weather(nick, loc) values (?,?)", (nick.lower(), loc))
        db.commit()
    return getWeather(loc,nick).encode('utf8', 'ignore')

@hook.command(autohelp=False)
def fuckingweather(inp, nick="", db=None):
    "fuckingweather <location> -- gets the fucking weather for you"
    db.execute("create table if not exists weather(nick primary key, loc)")

    if not inp:
        loc = db.execute("select loc from weather where nick=lower(?)", (nick,)).fetchone()
        if not loc:
            return fuckingweather.__doc__
        loc = loc[0]
    else:
        loc = inp
        db.execute("insert or replace into weather(nick, loc) values (?,?)", (nick.lower(), loc))
        db.commit()
    
    r = requests.get("http://thefuckingweather.com/",params={"where":loc,"unit":"c"})
    if r.status_code == requests.codes.ok:
        location = re.search("""<div style="float: left;"><span id="locationDisplaySpan" class="small">(.*)<\/span><\/div>""",r.text)
        temperature = re.search("""<span class="temperature" tempf="(.*)">(.*)<\/span>""",r.text)
        remark = re.search("""<p class="remark">(.*)<\/p>""",r.text)
        flavor = re.search("""<p class="flavor">(.*)<\/p>""",r.text)
        if location and temperature and remark and flavor:
            return u"%s, %s°C/%s°F, %s - %s"%(location.group(1),temperature.group(2),temperature.group(1),remark.group(1),flavor.group(1))
        else:
            return "I CAN'T FIND THAT SHIT"
