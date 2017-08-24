from flask import Flask, request, render_template
from twilio.twiml.voice_response import VoiceResponse, Dial
import arrow, re
app = Flask(__name__)

numbers = {
    "+19027071118":"+19027071118",
    "+19027019011":"traverseda",
}
users = {v:k for k,v in numbers.items()}

#domain="t8q-testing.sip.us1.twilio.com"
domain="t8q.sip.us1.twilio.com"
domains=["t8q.sip.us1.twilio.com","outsidecontext.solutions","t8q.org","t8q-testing.sip.us1.twilio.com"]
numberFromSip=re.compile("^sip:(?P<id>(?P<number>\+?[1-9]\d{1,14})|(?P<user>.*))@(?P<domain>.*)$")

from functools import wraps

@wraps(Dial.__init__)
def routedDialer(*args,**kwargs):
    sipFrom = numberFromSip.match(kwargs['caller_id'])
    if sipFrom and sipFrom.group('domain') in domains:
        if sipFrom.group('user') in users:
            kwargs['caller_id']=users[sipFrom.group('user')]
        elif sipFrom.group('number') in numbers:
            kwargs['caller_id']=sipFrom.group('number')
    elif sipFrom:
        del kwargs['caller_id']
    return Dial(*args,**kwargs)
def route(dialer,number):
    sipTo = numberFromSip.match(number)
    if sipTo and sipTo.group('number') in numbers:
        dialer.sip("sip:{}@{}".format(numbers[sipTo.group('number')],domain))
    elif sipTo and sipTo.group('user'):
        dialer.sip(request.values['To'])
    elif sipTo and sipTo.group('number'):
        dialer.number(sipTo.group('number'))
    else:
        dialer.number(request.values['To'])

@app.route('/phone/',methods=['GET', 'POST'])
def phone():
    print(request.values)
    resp = VoiceResponse()
    dial=routedDialer(caller_id=request.values['From'])
    route(dial,request.values['To'])
    resp.append(dial)
    print(resp)

    return str(resp)

def hello_world(template=None):
    print(request)
    print(request.values)
    context={
        'request':request,
        'values':request.values,
        'arrow':arrow,
        'numbers':numbers,
        'numberFromSip':numberFromSip,
    }
    t = render_template('phone.xml', **context)
    print(t)
    return t


if __name__ == "__main__":
    app.run()
