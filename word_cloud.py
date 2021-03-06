from wordcloud import WordCloud
import nltk
nltk.download('punkt')
from collections import Counter
import matplotlib.pyplot as plt
from flask import Flask, request, jsonify
from flask_restful import Api
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='outputs')
api = Api(app)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


font_path = 'SECRCODE.TTF'


def get_tags(text, max_count, min_length):
    is_noun = lambda pos: pos[:2] == 'NN'
    tokenized = nltk.word_tokenize(text)
    nouns = [word for (word, pos) in nltk.pos_tag(tokenized) if is_noun(pos)]
    processed = [n for n in nouns if len(n) >= min_length]
    count = Counter(processed)
    result = {}
    for n, c in count.most_common(max_count):
        result[n] = c
    if len(result) == 0:
        result["There is no content."] = 1
    return result


def make_cloud_image(tags, file_name):
    word_cloud = WordCloud(
        font_path=font_path,
        width=800,
        height=800,
        background_color="white",
    )
    word_cloud = word_cloud.generate_from_frequencies(tags)
    fig = plt.figure(figsize=(10, 10))
    plt.imshow(word_cloud)
    plt.axis("off")
    fig.savefig("outputs/{0}.png".format(file_name))


def process_from_text(text, max_count, min_length, words, file_name):
    tags = get_tags(text, int(max_count), int(min_length))
    for n, c in words.items():
        if n in tags:
            tags[n] = tags[n] * float(words[n])
    make_cloud_image(tags, file_name)


@app.route("/process", methods=['GET', 'POST'])
def process():
    content = request.json
    words = {}
    if content['words'] is not None:
        for data in content['words'].values():
            words[data['word']] = data['weight']
    process_from_text(content['text'], content['maxCount'], content['minLength'], words, content['textID'])
    result = {'result':True}
    return jsonify(result)


@app.route('/outputs', methods=['GET', 'POST'])
def output():
    text_id = request.args.get('textID')
    return app.send_static_file(text_id + '.png')


@app.route('/validate', methods=['GET', 'POST'])
def validate():
    text_id = request.args.get('textID')
    path = "outputs/{0}.png".format(text_id)
    result = {}
    if os.path.isfile(path):
        result['result'] = True
    else:
        result['result'] = False
    return jsonify(result)


if __name__ == '__main__':
    app.run('0.0.0.0', port=80, threaded=True)
