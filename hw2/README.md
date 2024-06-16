# HW 2

## Сборка
```
 docker build -t mtu_prober -f Dockerfile .
```

## Запуск
```
 docker run --platform linux/amd64 --rm -p 8080:8080 --dns 8.8.8.8 -e host=<your_host> -it mtu_prober
```
