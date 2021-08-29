## Запуск локально для разработки
Собираем образ (находясь в текущей директории frontend):
```shell
docker build -t search-frontend .
```

Чтобы запустить UI в dev-окружении:
```shell
docker run --rm -d -p 3000:3000 --name search-frontend search-frontendfrontend
```
Идём смотреть:
http://localhost:3000/

Чтобы остановить:
```shell
docker stop search-frontend
```

## Запуск продакшен контейнера
Собираем образ (находясь в текущей директории frontend):
```shell
docker build -f Dockerfile.prod -t search-frontend-prod .
```

Чтобы запустить UI в prod-окружении:
```shell
docker run --rm -d -p 80:80 --name search-frontend-prod search-frontend-prod
```

Идём смотреть:
http://localhost/

Чтобы остановить:
```shell
docker stop search-frontend-prod
```
