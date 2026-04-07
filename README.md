# Как запустить:
## 1. Зайдите в командную строку и введите:

wsl -d Ubuntu

cd /mnt/c/l_a_b

python3 -m venv venv

source venv/bin/activate

## 2. Активируйте WSL интеграцию в Docker Desktop

## 3. Запустите проект в командной строке (в WSL):

./memory_limits.sh

./run.sh

## Чтобы запустить приложение заново, введите команды:

docker stop $(docker ps -aq) 2>/dev/null

docker rm $(docker ps -aq) 2>/dev/null

docker network prune -f

docker volume prune -f
