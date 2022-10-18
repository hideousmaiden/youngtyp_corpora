# youngtyp_corpora


- обкачать типологов
- распарсить пдфки в текст
- разобрать и положить в бд
- интерфейс поиска


### Структура БД
- **texts**:
    id_text, text
- **meta**: id_text, author, topic, year, affilation, contacts, abbr text
- **links**: id_text, id_link, link
- **glosses**: id_text, id_gloss, gloss
- **sents**:
    id_text, id_sent, sent
- **words**:
    id_text, id_sent, id_word, word, lemma, pos

NB: везде нумерация по id вложенная, т.е. id_sent и т.п. обнуляется для каждого нового текста
