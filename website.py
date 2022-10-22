import sqlite3
import pandas as pd
import numpy as np
from flask import Flask
from flask import render_template
import sys
import os

from flask import request, redirect, url_for
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
# from password import password

import re
import pymorphy2
morph = pymorphy2.MorphAnalyzer()

app = Flask(__name__)

# create_engine('sqlite:///{}'.format('youngtyp.db'), connect_args={'timeout': 15})
DATABASE = 'youngtyp.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE}'
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# keyword = password

conn = sqlite3.connect(DATABASE)
cur = conn.cursor()

#создать таблицы в базе данных

cur.execute("""
CREATE TABLE IF NOT EXISTS searches
(id INTEGER PRIMARY KEY AUTOINCREMENT, text text) 
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS texts
(id_text int, text text)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS meta
(id_text int, author text, topic text, year int, affilation text, contacts text, abbr text) 
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS sents 
(id_text int, id_sent int, sent text) 
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS words
(id_text int, id_sent int, id_word int, word text, lemma text, pos text)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS links
(id_text int, id_link int, link text) 
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS glosses
(id_text int, id_gloss int, raw text, gloss text, translation text) 
""")

# conn.commit()
# conn.close()

path = ''

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/no_result')
def no_result():
    return render_template('no_result.html')

@app.route('/credits')
def credits():
    return render_template('credits.html')
    
class Search(db.Model):
    __tablename__ = 'searches'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    
class Words(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    id_text = db.Column(db.Integer)
    id_sent = db.Column(db.Integer)
    id_word = db.Column(db.Integer)
    word = db.Column(db.Text)
    lemma = db.Column(db.Text)
    pos = db.Column(db.Text)
        
@app.route('/process', methods=['GET', 'POST'])
def answer_process():
    if request.method == 'POST' or not request.args:
        return redirect(url_for('home'))
    text = request.args.get('search')
    search = Search(
        text=text
    )
    db.session.add(search)
    db.session.commit()
    db.session.refresh(search)

    return redirect(url_for('search_result'))

def process_query(query, limit=10):
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
    ask = {1:'''SELECT words.id_text, words.id_sent, words.id_word, words.word FROM words
  JOIN words_right ON words_right.id_sent=words.id_sent AND words_right.id_text=words.id_text AND id_word_right = (id_word + 1)
  JOIN words_rright ON words_rright.id_sent=words.id_sent AND words_rright.id_text=words.id_text AND id_word_rright = (id_word + 2)
  WHERE {} COLLATE NOCASE
  LIMIT {};''', 2:'''SELECT words.id_text, words.id_sent, words.id_word, words.word, id_word_right, word_right FROM words
  JOIN words_right ON words_right.id_sent=words.id_sent AND words_right.id_text=words.id_text AND id_word_right = (id_word + 1)
  JOIN words_rright ON words_rright.id_sent=words.id_sent AND words_rright.id_text=words.id_text AND id_word_rright = (id_word + 2)
  WHERE {} COLLATE NOCASE
  LIMIT {}
  ;''', 3:'''SELECT words.id_text, words.id_sent, words.id_word, words.word, id_word_rright, word_rright FROM words
  JOIN words_right ON words_right.id_sent=words.id_sent AND words_right.id_text=words.id_text AND id_word_right = (id_word + 1)
  JOIN words_rright ON words_rright.id_sent=words.id_sent AND words_rright.id_text=words.id_text AND id_word_rright = (id_word + 2)
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
    done = [ele for ele in db.engine.execute(ask)]
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
    left = sents[id_sent][:id_word][::-1]
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
    right = sents[id_sent][id_word+1:]
    id_sent += 1
    while len(right) < length and id_sent < len(sents):
        n_needed = length - len(right)
        if len(sents[id_sent]) < n_needed:
            n_needed = len(sents[id_sent])
        fetch = sents[id_sent][:n_needed]
        right += fetch
        id_sent += 1
    return ' '.join(right)

@app.route('/search_result')
def search_result():
    text = db.session.query(Search.text).order_by(Search.id.desc()).where(Search.text != None).first()[0]
    results = process_query(text)
    
    outputs = []
    for result in results:
        id_sents = [ele[0] for ele in db.engine.execute(
                f'''
                SELECT DISTINCT id_sent FROM words WHERE id_text={result['id_text']}
                ''')]
        sents = [[ele[0] for ele in db.engine.execute(
                f'''
                SELECT DISTINCT word FROM words WHERE id_text={result['id_text']}
                                            AND id_sent={id_sent}
                ''')] for id_sent in id_sents]
        
        meta = [ele for ele in db.engine.execute(
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
    
    if outputs == []:
        return render_template('no_result.html')
    else:
        return render_template('output.html', outputs=outputs)

if __name__ == '__main__':
    app.run(debug=False)