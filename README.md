# youngtyp_corpora

Это корпус, собранный из тезисов на Конференцию по типологии и грамматике для молодых исследователей, которая проводится в Санкт-Петербурге и также известна просто как Молодые типологи.

> [корпус](http://thnlgrlivrlvdwsbrnwthrssnhrys.pythonanywhere.com/)

> [сайт конференции](https://youngconfspb.com/glavnaya)

> [база с текстами](https://drive.google.com/file/d/1Trcg6-ziFgyHn8IEEjevkDtIBRPro_Ph/view?usp=sharing)

### Сбор данных
По результатам каждой конференции публкуется сборник тезисов в формате .pdf. Мы собрали тесты тезисов и соответствующую им метаинформацию TO DO: КАК

### Парсинг
Частеречную разметку мы сделали [моделью](http://docs.deeppavlov.ai/en/master/features/models/morphotagger.html) от ***deepavlov***, а лемматизацию - при помощи pymorpy2.
Размеченные тексты хранятся в базе данных SQLAlchemy.

### Поиск
Максимальное количество токенов(слов) в поисковом запросе - 3. Поиск ведётся по точным формам, леммам и POS-тэгам через таблицу, где каждому слову соответствуют его значения, а также 2 соседа справа и их значения.


### Структура БД
- **texts**:
    id_text, text
- **meta**: id_text, author, topic, year, affilation
- **sents**:
    id_text, id_sent, sent
- **words**:
    id_text, id_sent, id_word, word, lemma, pos
- **words_right**:
    id_text, id_sent, id_word, word_right, lemma_right, pos_right
- **words_rright**:
    id_text, id_sent, id_word, word_rright, lemma_rright, pos_rright

NB: везде нумерация по id вложенная, т.е. *id_sent* и т.п. обнуляется для каждого нового текста
