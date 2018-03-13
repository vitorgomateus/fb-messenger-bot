import os
import sys
import json
import time
from datetime import datetime

import requests
from flask import Flask, request
from woocommerce import API
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
    log("_DATA_")
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    # VTOR
    # if data["object"] == "page":
    #     for entry in data["entry"]:
    #         for messaging_event in entry["messaging"]:
    #             if messaging_event["message"].get("is_echo"):
    #                 log("WE GOT ECHO")
    #
    #strdata = str(data)
    #strdata= json.dumps(data)
    #if "standby" in strdata:
       #log("WE HAVE STANBY")
    #
    #time.sleep(300) 
    # if data["object"] == "page":

    #   original
    if data["object"] == "page":
        for entry in data["entry"]:

            if entry.get("standby"):
                for standby_event in entry["standby"]:  # a message was sent in standby
                    log("STANBY EVENT")

            elif entry.get("messaging"):

                for messaging_event in entry["messaging"]:
                    sender_id_pass = messaging_event["sender"]["id"]

                    if messaging_event.get("message"):  # someone sent us a message
                        sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                        recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID

                        if messaging_event["message"].get("attachments"):
                            log("Bot got a sticker!")
                        else:
                            message_text = messaging_event["message"]["text"]  # the message's text
                            if message_text == "produtos":
                                get_send_products(0, sender_id)
                            else:
                               send_message(sender_id, "BOT :D")
                               pass

                    if messaging_event.get("request_thread_control"):  # ADMIN requested control
                        log("ADMIN REQUEST CONTROL sender_id={sendr}".format(sendr=sender_id_pass))
                        pass_thread_control(sender_id_pass)

                    if messaging_event.get("request_thread_control"):  # ADMIN control passed
                        log("PASS CONTROL TO ADMIN")
                        
                    if messaging_event.get("delivery"):  # delivery confirmation
                        pass

                    if messaging_event.get("optin"):  # optin confirmation
                        pass

                    if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                        pass

            else:
                log("DEVDO - No Standby, neither Messaging")
    else:
        log("DEVDO - no PAGE")

    return "ok", 200


def send_message(recipient_id, message_text):

#       intact -v-
    log("SENDing message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

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
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)

def get_send_products(category, recipient):
    log("NO* REQUEST PRODUCTS cat={cate}".format(cate=category))

    

    wc_api_mfip = API(
        url="https://myfriendsinportugal.com",
        consumer_key= os.environ["WC_CONSUMER_KEY"],
        consumer_secret= os.environ["WC_CONSUMER_SECRET"],
        wp_api=True,
        version="wc/v2",
        query_string_auth=True 
    )
    #query_string_auth=True // Force Basic Authentication as query string true and using under HTTPS

    w = wc_api_mfip.get("products?status=publish")
     #"name": "Ship Your Idea",

    #"permalink": "https://example.com/product/ship-your-idea-22/",
   # "images": [
   # "src": "https://example.com/wp-content/uploads/2017/03/T_4_front-11.jpg",
    response_products = w.json()
    log("WC_RESPONSE ? ")
    log(response_products[0]["name"])
    #log(w.text)


    arr_title=[]
    arr_title[0]=response_products[0]["name"]
    arr_title[1]=response_products[1]["name"]
    arr_title[2]=response_products[2]["name"]
    arr_image=[]
    arr_image[0]=response_products[0]["images"][0]["src"]
    arr_image[1]=response_products[1]["images"][0]["src"]
    arr_image[2]=response_products[2]["images"][0]["src"]
    arr_link=[]
    arr_link[0]=response_products[0]["permalink"]
    arr_link[1]=response_products[1]["permalink"]
    arr_link[2]=response_products[2]["permalink"]
    send_webview( arr_title, arr_image, arr_link, recipient)



def send_webview(title_arr, img_arr, url_arr, recipient_id):
    log("NO* SEND_WEBVIEW")
    # iterate through arr...
    paramsWebview = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headersWebview = {
        "Content-Type": "application/json"
    }
    dataWebview = json.dumps({
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
                    "title":title_arr[0],
                    "image_url":img_arr[0],
                    "subtitle":"",
                    "buttons":[
                        {
                            "type":"web_url",
                            "url":url_arr[0],
                            "title":"consultar"
                          }          
                    ]      
                  },
                  {
                    "title":title_arr[1],
                    "image_url":img_arr[1],
                    "subtitle":"",
                    "buttons":[
                        {
                            "type":"web_url",
                            "url":url_arr[1],
                            "title":"consultar"
                          }             
                    ]      
                  },
                  {
                    "title":title_arr[2],
                    "image_url":img_arr[2],
                    "subtitle":"",
                    "buttons":[
                        {
                            "type":"web_url",
                            "url":url_arr[2],
                            "title":"consultar"
                          }             
                    ]      
                  }
                ]
              }
            }
        }
    })
    wv = requests.post("https://graph.facebook.com/v2.6/me/messages", params=paramsWebview, headers=headersWebview, data=dataWebview)
    if wv.status_code != 200:
        log(wv.status_code)
        log(wv.text)

def pass_thread_control(chatter_id):
    passData = json.dumps({
        "recipient": {
            "id": chatter_id
        },
        "target_app_id": 263902037430900,
        "metadata": "-X pass_thread_control X-" 
    })
    passParams = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"],
    }
    passHeaders = {
        "Content-Type": "application/json"
    }
    hj = requests.post("https://graph.facebook.com/v2.6/me/pass_thread_control", params=passParams, headers=passHeaders, data=passData)
    
    if hj.status_code != 200:
        log(hj.status_code)
        log(hj.text)
    else:
        log("HANDOVER")



def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku 

                                ### This function is giving me errors, but it's not clear what the problem is.
                                ### I always call it with only one parameter, a string or a 'dict', 
                                ###     and usually there is no problem.
                                ### but when I call it to log the http response is when errors show up.
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        #else:
            #msg = unicode(msg).format(*args, **kwargs) ### If I comment this line, no error shows up
            #msg=msg
        print u"{}: {}".format(datetime.now(), msg)
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
