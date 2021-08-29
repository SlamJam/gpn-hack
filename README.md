GPN Tech.Challenge команды Object43
===================================

Создаём в корне проекта файл `luigi.cfg` на основе `datamining-toolbox/luigi.cfg.sample`.

Креды от _S3_ берём в _Gdrive_ в доке `Infra`.

Запускаем проект:

`$ docker-compose up --build --remove-orphans`

Реиндексация будет запускаться раз в минуту. Если в Эластике есть коллекция _**companies**_ ничего не произойдёт.
Если её нет, то будет создана и все документы будут индексированы в ней.

Полезные ссылки
---------------

После запуска проета доступны следующие веб-мордашки:

- [Luigi Scheduler Dashboard](http://localhost:8082)
- [ElasticHQ](http://localhost:8001)
- [Elasticvue](http://localhost:8002)
- [ElasticsearchComrade](http://localhost:8003)
