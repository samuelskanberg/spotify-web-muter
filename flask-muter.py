#!/usr/bin/env python3
from flask import Flask, request
from flask_cors import CORS
import argparse
import sys
import subprocess
app = Flask(__name__)
CORS(app)

contains = ""

javascript_to_paste_template = """
function postChangedTitle(title) {
    var xhr = new XMLHttpRequest();
    var url = "URL_PLACE_HOLDER";
    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            var response = xhr.responseText;
            console.log("Response: "+response);
        }
    };
    var data = JSON.stringify({"title": title });
    xhr.send(data);
}
new MutationObserver(function() {
    console.log("New title:" +document.title);
    postChangedTitle(document.title);
}).observe(document.querySelector('title'),{ childList: true });
"""

def mute():
    print("Muting")
    cm = ["amixer", "-q", "-D", "pulse", "sset", "Master", "off"]
    subprocess.Popen(cm)

def unmute():
    print("Unmuting")
    cm = ["amixer", "-q", "-D", "pulse", "sset", "Master", "on"]
    subprocess.Popen(cm)

@app.route("/", methods=['POST'])
def hello():
    data = request.json
    if "title" not in data:
        return "No title supplied"
    title = data['title']
    print("Title is: {}".format(title))
    print("Title should contain: {}".format(contains))
    if contains in title:
        unmute()
        return "Unmute"
    else:
        mute()
        return "Mute"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("contains", type=str,
                    help="A text which the title should contain")
    parser.add_argument("-p", "--port", type=int, default=5000,
                    help="Port number the webserver will run under")
    args = parser.parse_args()

    contains = args.contains
    port = args.port
    print("Contains is: {}".format(contains))
    print("Port is: {}".format(port))

    javascript_to_paste = javascript_to_paste_template.replace("URL_PLACE_HOLDER", "http://127.0.0.1:{}/".format(port))
    print("Paste the following in the console: \n {} \n\n".format(javascript_to_paste))

    app.run(host='0.0.0.0', port=port, debug=True)
