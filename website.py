from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import logging

logging.basicConfig(filename='problems.log', level=logging.DEBUG)

from sqlalchemy import create_engine
# from models import db

import re
import pymorphy2

morph = pymorphy2.MorphAnalyzer()

DATABASE = 'youngtyp.db'
# create the extension
db = SQLAlchemy()
# create the app
app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DATABASE}"
# initialize the app with the extension
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)

with app.app_context():
    db.create_all()

engine = create_engine('sqlite:///youngtyp.db', connect_args={"check_same_thread": False})
conn = engine.connect()

path = ''

class Search(db.Model):
    __tablename__ = 'searches'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    order_year = db.Column(db.Integer)

class Words(db.Model):
    __tablename__ = 'big_words'
    id = db.Column(db.Integer, primary_key=True)
    id_text = db.Column(db.Integer)
    id_sent = db.Column(db.Integer)
    id_word = db.Column(db.Integer)
    word = db.Column(db.Text)
    lemma = db.Column(db.Text)
    pos = db.Column(db.Text)
    id_word_right = db.Column(db.Integer)
    word_right = db.Column(db.Text)
    lemma_right = db.Column(db.Text)
    pos_right = db.Column(db.Text)
    id_word_rright = db.Column(db.Integer)
    word_rright = db.Column(db.Text)
    lemma_rright = db.Column(db.Text)
    pos_rright = db.Column(db.Text)

class Texts(db.Model):
    __tablename__ = 'texts'
    id_text = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)

class Sents(db.Model):
    __tablename__ = 'sents'
    # __table_args__ = {'extend_existing': True}
    id_text = db.Column(db.Integer)
    id_sent = db.Column(db.Integer, primary_key=True)
    sent = db.Column(db.Text)

class Meta(db.Model):
    __tablename__ = 'meta'
    id_text = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    author = db.Column(db.Text)
    topic = db.Column(db.Text)
    affiliation = db.Column(db.Text)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/no_result')
def no_result():
    return render_template('no_result.html')

@app.route('/credits')
def credits():
    return render_template('credits.html')

@app.route('/instructions')
def instructions():
    return render_template('instructions.html')

@app.route('/process', methods=['GET', 'POST'])
def answer_process():
    if request.method == 'POST' or not request.args:
        return redirect(url_for('home'))
    text = request.args.get('search')
    order_year = request.args.get('order_year')
    print(order_year)
    results = process_query(text, order_year=order_year)

    outputs = []
    for result in results:
        id_sents = [ele[0] for ele in conn.execute(
                f'''
                SELECT DISTINCT id_sent FROM sents WHERE id_text={result['id_text']}
                ''')]
        sents = [[ele[0] for ele in conn.execute(
                f'''
                SELECT DISTINCT word FROM big_words WHERE id_text={result['id_text']}
                                            AND id_sent={id_sent}
                ''')] for id_sent in id_sents]
        print([(id_sents[i], sents[i]) for i in range(len(id_sents))], '\n\n\n')

        meta = [ele for ele in conn.execute(
                f'''
                SELECT DISTINCT author, topic, year, affilation
                FROM meta WHERE id_text={result['id_text']}
                ''')][0]

        output = dict()
        output['right'] = make_right(sents, result['id_sent'], result['last_word_id'], length=5)
        output['left'] = make_left(sents, result['id_sent'], result['id_word'], length=5)
        output['pattern'] = result['pattern']
        output['author'] = meta[0]
        output['topic'] = meta[1]
        output['year'] = meta[2]
        output['affiliation'] = meta[3]
        outputs.append(output)
    logging.info(f'outputs: {outputs}')

    if outputs == []:
        return render_template('no_result.html')
    else:
        return render_template('output.html', outputs=outputs)

    # return redirect(url_for('search_result'))

def process_query(query, order_year, limit=10):
    """
  process cql query

  args:
    query: str,
  returns:
    result: list of dict, list of dictionaries containing found results
      pattern: str, found pattern
      id_sent: int,
      id_text: int,
      id_word: int
      (last_word_id: int)
    """
# токены разделены словами
    parts = query.split(' ')
  # условия разделены плюсами
    conds = list(map(lambda x: x.split('+'), parts))
    pos_tr = {0:'pos',1:'pos_right', 2:'pos_rright'}
    lemma_tr = {0:'lemma',1:'lemma_right', 2:'lemma_rright'}
    word_tr = {0:'word',1:'word_right', 2:'word_rright'}
    que = []
    if order_year:
        ask = {1:'''SELECT id_text, id_sent, id_word, word FROM big_words
      WHERE {} COLLATE NOCASE
      ORDER BY id_text ASC
      LIMIT {};''', 2:'''SELECT id_text, id_sent, id_word, word, id_word_right, word_right FROM big_words
      WHERE {} COLLATE NOCASE
      ORDER BY id_text ASC
      LIMIT {}
      ;''', 3:'''SELECT id_text, id_sent, id_word, word, id_word_rright, word_rright FROM big_words
      WHERE {} COLLATE NOCASE
      ORDER BY id_text ASC
      LIMIT {}'''}
    else:
        ask = {1:'''SELECT id_text, id_sent, id_word, word FROM big_words
      WHERE {} COLLATE NOCASE
      LIMIT {};''', 2:'''SELECT id_text, id_sent, id_word, word, id_word_right, word_right FROM big_words
      WHERE {} COLLATE NOCASE
      LIMIT {}
      ;''', 3:'''SELECT id_text, id_sent, id_word, word, id_word_rright, word_rright FROM big_words
      WHERE {} COLLATE NOCASE
      LIMIT {}'''}
  # по словам
    for nn, ques in enumerate(conds):
        for cond in ques:
      #все условия для одного слова
            if re.match('[A-Z]+', cond):

                que.append('{} = "{}"'.format(pos_tr[nn], cond))
            elif re.match(r'".+"', cond):
                que.append('(({} = {}) '.format(word_tr[nn], cond) + 'OR ({} = {}) '.format(word_tr[nn], cond.lower()) + 'OR ({} = {}))'.format(word_tr[nn], cond.title()))
          #que.append('{} = {}'.format(word_tr[nn], cond))
            else:
                que.append('{} = "{}"'.format(lemma_tr[nn], morph.parse(cond)[0].normal_form))
    big_que = ' AND '.join(que)
    ask = ask[len(conds)].format(big_que, limit)
    done = [ele for ele in conn.execute(ask)]
    result = []
    for res in list(done):
        dd = dict()
        dd['pattern'] = ' '.join(list(filter(lambda x: str(x).isalpha(), res)))
        dd['id_sent'] = res[1]
        dd['id_text'] = res[0]
        dd['id_word'] = res[2]
        if len(res) > 4:
            dd['last_word_id'] = res[-2]
        else:
            dd['last_word_id'] = dd['id_word']
        result.append(dd)
    return result

def make_left(sents, id_sent, id_word, length=5):
    try:
        left = sents[id_sent][:id_word][::-1]
    except IndexError:
        return 'AAAA AAAA'
    id_sent -= 1
    while len(left) < length and id_sent >= 0:
        n_needed = length - len(left)
        if len(sents[id_sent]) < n_needed:
            n_needed = len(sents[id_sent])
        fetch = sents[id_sent][-n_needed::]
        left += reversed(fetch)
        id_sent -= 1
    return ' '.join(left[::-1])

def make_right(sents, id_sent, id_word, length=5):
    try:
        if id_word + 1 == len(sents[id_sent]):
            right = sents[id_sent][id_word+1:]
        else:
            right = []
    except IndexError:
        return 'AAAA AAAA'
    id_sent += 1
    while len(right) < length and id_sent < len(sents):
        n_needed = length - len(right)
        if len(sents[id_sent]) < n_needed:
            n_needed = len(sents[id_sent])
        fetch = sents[id_sent][:n_needed]
        right += fetch
        id_sent += 1
    return ' '.join(right)

if __name__ == '__main__':
    app.run(debug=False)