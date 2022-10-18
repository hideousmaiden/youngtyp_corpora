# youngtyp_corpora


- обкачать типологов
- распарсить пдфки в текст
- разобрать и положить в бд
- интерфейс поиска


### Структура БД
- **texts**:
    id_text, text
- **sents**:
    id_text, id_sent, sent
- **words**:
    id_text, id_sent, id_word, word, lemma, pos
