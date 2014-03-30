# -- coding: utf-8 --
from util import hook, http
import re, HTMLParser, urllib, random

def getTranslation(f,t,m):
    url = "http://translate.google.com/translate_a/t?"+urllib.urlencode({"client":"p","sl":f,"tl":t,"q":m})
    try:
        data = http.get_json(url.encode("utf8","ignore"))
    except http.HTTPError, e:
        return (str(e))
    if "dict" in data:
        return data["dict"][0]["entry"][0]["word"]
    else:
        return data["sentences"][0]["trans"]

@hook.command
def chat(inp, say=None):
    "chat <text> -- talk to a random bot."
    t = "en"
    f = "auto"
    m = inp.encode("utf8","ignore")
    regex = re.compile("\x1f|\x02|\x03(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)
    m = regex.sub("",m)
    langs = {'Swahili': 'sw', 'Swedish': 'sv', 'Hausa': 'ha', 'Icelandic': 'is', 'Javanese': 'jw', 'Estonian': 'et', 'Telugu': 'te', 'Turkish': 'tr', 'Marathi': 'mr', 'Italian': 'it', 'Azerbaijani': 'az', 'Slovenian': 'sl', 'Japanese': 'ja', 'Gujarati': 'gu', 'Polish': 'pl', 'Hindi': 'hi', 'Spanish': 'es', 'Dutch': 'nl', 'Hmong': 'hmn', 'Norwegian': 'no', 'Korean': 'ko', 'Russian': 'ru', 'Danish': 'da', 'Bulgarian': 'bg', 'Lao': 'lo', 'Somali': 'so', 'Finnish': 'fi', 'Hungarian': 'hu', 'Macedonian': 'mk', 'Welsh': 'cy', 'Bosnian': 'bs', 'Georgian': 'ka', 'Khmer': 'km', 'Malay': 'ms', 'French': 'fr', 'Catalan': 'ca', 'Maori': 'mi', 'Armenian': 'hy', 'Romanian': 'ro', 'Maltese': 'mt', 'Thai': 'th', 'Afrikaans': 'af', 'Tamil': 'ta', 'Punjabi': 'pa', 'Cebuano': 'ceb', 'Bengali': 'bn', 'Nepali': 'ne', 'Filipino': 'tl', 'Vietnamese': 'vi', 'Albanian': 'sq', 'Hebrew': 'iw', 'Indonesian': 'id', 'Greek': 'el', 'Haitian Creole': 'ht', 'Latin': 'la', 'Latvian': 'lv', 'English': 'en', 'Serbian': 'sr', 'Esperanto': 'eo', 'Croatian': 'hr', 'Portuguese': 'pt', 'Irish': 'ga', 'Zulu': 'zu', 'Chinese': 'zh-CN', 'Czech': 'cs', 'Ukrainian': 'uk', 'Igbo': 'ig', 'Belarusian': 'be', 'Kannada': 'kn', 'Galician': 'gl', 'German': 'de', 'Persian': 'fa', 'Slovak': 'sk', 'Mongolian': 'mn', 'Basque': 'eu', 'Urdu': 'ur', 'Lithuanian': 'lt', 'Arabic': 'ar', 'Yoruba': 'yo', 'Yiddish': 'yi'}
    ll = []
    nl = []
    langs_ = langs.values()
    for x in range(0,5):
        rnd = random.randint(0,len(langs_)-1)
        ll.append(langs_[rnd])
    ll.append("en")
    last_lang = "auto"
    for lang in ll:
        m = getTranslation(last_lang,lang,m).encode("utf8","ignore")
        #say("last_lang: "+last_lang+" lang: "+lang+" m: "+m.decode("utf8","ignore"))
        #say(lang+" "+m.decode("utf8","ignore"))
        last_lang = lang
    #say("Input: \002%s\002 Output: \002%s\002"%(inp,m))
    #say("Translated through: %s"%(",".join(ll)))
    return m
