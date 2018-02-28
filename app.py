import os
import sys
import json
from datetime import datetime

import requests
from flask import Flask, request
#from funcao import send_message

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello earth, it's alive!!!!", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    send_message(sender_id, "I'm okay.")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

#       vitor
    # mkm = requests.get("https://jsonplaceholder.typicode.com/posts/1", params={}, headers={
    #     "Content-Type": "application/json"
    # }, data={})
    # if mkm.status_code != 200:
    #     log(r.status_code)
    #     log(r.text)
    # etv = mkm.get_json
    # tve = resquest.data.get_json
    # vet = mkm.request.data.get_json
    # vavet = message_text + vet[body]
    # log("response is mkm.get_json={one}; resquest.data.get_json = {two};  mkm.request.data.get_json= {three}; message_text + vet[body]={four}".
    #     format(one=etv, two=tve, three=vet, four=vavet))
#   end vitor





#       intact -v-
    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message":{
            "attachment":{
              "type":"template",
              "payload":{
                "template_type":"generic",
                "elements":[
                   {
                    "title":"Welcome!",
                    "image_url":"https://images.pexels.com/photos/287487/pexels-photo-287487.jpeg?w=1260&h=750&auto=compress&cs=tinysrgb",
                    "subtitle":"We have the right explosion for everyone.",
                    "default_action": {
                      "type": "web_url",
                      "url": "https://myfriendsinportugal.com/",
                      "messenger_extensions": false,
                      "webview_height_ratio": "tall",
                      "fallback_url": "https://myfriendsinportugal.com/"
                    },
                    "buttons":[
                      {
                        "type":"web_url",
                        "url":"https://myfriendsinportugal.com",
                        "title":"View Website"
                      },{
                        "type":"postback",
                        "title":"Start Chatting",
                        "payload":"DEVELOPER_DEFINED_PAYLOAD"
                      }              
                    ]      
                  }
                ]
              }
            }
  }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        else:
            msg = unicode(msg).format(*args, **kwargs)
        print u"{}: {}".format(datetime.now(), msg)
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
