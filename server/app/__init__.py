from flask import Flask, render_template, jsonify, request
import requests
import json

app = Flask(__name__)

#@app.route('/')
@app.route('/tasteful')
@app.route('/tasteful/index', methods=['GET'])
def index():
    title = 'Index'
    sources = ['red\dit', 'github', 'stackoverflow']
    metrics = ['answers', 'forks', 'upvotes']

    return render_template('index.html',
                            title=title,
                           sources=sources,
                           metrics=metrics)

@app.route('/scrape')
def scrape():
    #r = requests.get('https://reddit.com/user/cegal/overview.json')
    data = {"a":"b"}
    return jsonify(data)
