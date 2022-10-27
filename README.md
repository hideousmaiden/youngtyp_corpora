# youngtyp_corpora


Это корпус, собранный из тезисов на *Конференцию по типологии и грамматике для молодых исследователей*, которая проводится в Санкт-Петербурге и также известна просто как *Молодые типологи*.

> [Онлайн-корпус](http://thnlgrlivrlvdwsbrnwthrssnhrys.pythonanywhere.com/)<br>[База с текстами](https://drive.google.com/file/d/1hXHzqmE_ef4xUWuDMoiZIfqAtedDUBRs/view?usp=sharing)

## Навигация по папке

:pushpin: [`static`](/static), [`templates`](/templates), [`website.py`](/website.py) — файлы, с которыми работает сайт: изображения, HTML-страницы и код на Flask (Саша Шикунова)<br>
:pushpin: [`requirements.txt`](/requirements.txt) — библиотеки, нужные для работы сайта<br>
:pushpin: [`youngtyp_corpora_crawling+extracting.ipynb`](/youngtyp_corpora_crawling+extracting.ipynb) — тетрадка с парсингом и предобработкой PDF (Катя Козлова)<br>
:pushpin: [`youngtyp.json`](/youngtyp.json) — файл с результатами парсинга PDF<br>
:pushpin: [`youngtyp.db`](/youngtyp.db) — уменьшенная демонстрационная база данных<br>
:pushpin: [`youngtyp_corpora_parsing+sql.ipynb`](/youngtyp_corpora_parsing+sql.ipynb) — тетрадка с разработкой поиска (Даша Сидоркина)

## Этапы работы
### Сбор данных
По результатам каждой конференции публкуется сборник тезисов в формате `.pdf`. Мы краулерили машиночитаемые тезисники с [сайта конференции](https://youngconfspb.com/glavnaya) и извлекали текст при помощи [`pdfplumber`](https://github.com/jsvine/pdfplumber). Потом чистили, делили сборники на отдельные тезисы, а также собирали соответствующую им метаинформацию (*год конференции*, *автор_ы*, *аффилиация/и*, *название*). Первичная предобработка осуществлялась при помощи regexp, повторяющихся частей и здравого смысла, а потом данные чистились вручную.

### Парсинг
Частеречную разметку мы сделали [моделью](http://docs.deeppavlov.ai/en/master/features/models/morphotagger.html) от [`deepavlov`](https://github.com/deeppavlov/DeepPavlov), а лемматизацию — при помощи [`pymorpy2`](https://pymorphy2.readthedocs.io/en/stable/).
Размеченные тексты хранятся в базе данных SQLAlchemy.

### Поиск
Максимальное количество токенов (слов) в поисковом запросе — 3. Поиск ведётся по точным формам, леммам и POS-тэгам через таблицу, где каждому слову соответствуют его значения, а также 2 соседа справа и их значения.


### Структура базы данных
- **texts**:<br>
        *id_text, text*
- **meta**:<br>
        *id_text, author, topic, year, affilation*
- **sents**:<br>
        *id_text, id_sent, sent*
- **words**:<br>
        *id_text, id_sent, id_word, word, lemma, pos, word_right, lemma_right, pos_right, word_rright, lemma_rright, pos_rright*

**NB!** нумерация по id везде вложенная, т.е. *id_sent* и т.п. обнуляется для каждого нового текста

### Сайт
Онлайн-версия корпуса состоит из 3-х страниц:
:page_with_curl: **главной страницы**, где осуществляется поиск;<br>
:page_with_curl: страницы с описанием тэгов и того, как делать запрос;<br>
:page_with_curl: страницы с описанием авторов и самого корпуса

## Авторы
:telephone_receiver: [*Саша Шикунова*](https://t.me/thnlgrlivrlvdwsbrnwthrssnhrys)<br>
:telephone_receiver: [*Даша Сидоркина*](https://t.me/hideousmaiden)<br>
:telephone_receiver: [*Катя Козлова*](https://t.me/da_budet_tak)<br>
