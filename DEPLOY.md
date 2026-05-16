# Развёртывание library-constructor

В репозитории три compose-файла под разные сценарии:

| Файл                              | Когда использовать                                          |
| --------------------------------- | ----------------------------------------------------------- |
| `docker-compose.codespaces.yaml`  | **GitHub Codespaces без своего домена** (быстрый запуск)    |
| `docker-compose.tunnel.yaml`      | Codespaces с привязкой собственного домена через CF Tunnel  |
| `docker-compose.yaml`             | VPS / выделенный сервер с публичным IP и портами 80/443     |

> **Важно (безопасность).** В исходном репозитории `plenilla/library-constructor` в публичный доступ были закоммичены реальный API-токен Cloudflare и приватные SSL-ключи `exhibitdes.ru`. Перед использованием:
> - Отзовите старый токен в Cloudflare Dashboard → My Profile → API Tokens.
> - Если у вас есть доступ к exhibitdes.ru, отзовите старые сертификаты Let's Encrypt.
> - В этой версии репозитория секреты вынесены в `.env` и `cloudflare.ini` (оба в `.gitignore`).

---

## Сценарий 1 — GitHub Codespaces без своего домена (самый простой)

Подходит, если нужно просто посмотреть/потестить. Сайт будет доступен по выданному Codespaces URL вида `https://<codespace-name>-3000.app.github.dev`.

### Шаги

1. **Откройте репозиторий в Codespace.** На странице репозитория на GitHub: `Code` → `Codespaces` → `Create codespace on main`.

2. **В терминале Codespace:**

   ```bash
   cp .env.example .env
   mkdir -p storage/photos

   docker compose -f docker-compose.codespaces.yaml up --build -d
   ```

   Первая сборка займёт 2–4 минуты (npm install + next build + python deps).

3. **Сделайте порты публичными.** В VS Code (вкладка `PORTS` снизу):

   - Найдите порт `3000` (frontend) → правый клик → `Port Visibility` → `Public`.
   - То же самое для порта `8000` (backend).
   - При желании — порт `8080` (Adminer).

   Без этого браузер не сможет дёргать API из-за приватной аутентификации Codespaces.

4. **Откройте URL фронтенда.** Рядом с портом `3000` в той же вкладке кликните на иконку глобуса. Откроется `https://<codespace-name>-3000.app.github.dev`.

### Как это работает

- HTTPS даёт сам Codespaces — нужды в `nginx-proxy` и `certbot` нет.
- `CODESPACE_NAME` — переменная окружения, которую Codespace выставляет автоматически. Compose-файл подставляет её в `NEXT_PUBLIC_BASE_URL` (build-arg для Next.js) и в `ALLOWED_ORIGINS` (CORS бэкенда).
- При пересоздании Codespace его имя меняется — нужно пересобрать фронт: `docker compose -f docker-compose.codespaces.yaml up --build -d`.

### Известные ограничения Codespaces

- **Засыпает** через ~30 минут бездействия — после простоя первый запрос будет долгим.
- **Не для продакшена** — нет SLA, лимит часов в месяц на бесплатном тарифе.
- При смене Codespace меняется и URL — нужна пересборка фронтенда.

---

## Сценарий 2 — Codespaces + свой домен через Cloudflare Tunnel

Используйте `docker-compose.tunnel.yaml`, если нужен постоянный URL `https://rapidstream.ru` (но всё ещё хостинг в Codespaces). Cloudflare сам терминирует TLS и проксирует трафик внутрь docker-сети.

### 1. Подготовка Cloudflare

1. Зона `rapidstream.ru` должна быть в вашем аккаунте Cloudflare.
2. **Cloudflare Zero Trust** → **Networks** → **Tunnels** → **Create a tunnel** → **Cloudflared**.
3. Скопируйте токен туннеля (длинная строка `eyJ...`).
4. В **Public Hostnames** добавьте маршруты:

   | Subdomain | Domain          | Path     | Service                  |
   | --------- | --------------- | -------- | ------------------------ |
   | (пусто)   | rapidstream.ru  | (пусто)  | `http://frontend:80`     |
   | www       | rapidstream.ru  | (пусто)  | `http://backend:8000`    |
   | (пусто)   | rapidstream.ru  | `admin`  | `http://adminer:8080`    |

### 2. Запуск в Codespace

```bash
cp .env.example .env
# Впишите CLOUDFLARE_TUNNEL_TOKEN=<токен из шага 1.3>
mkdir -p storage/photos

docker compose -f docker-compose.tunnel.yaml up --build -d
docker compose -f docker-compose.tunnel.yaml logs -f cloudflared
```

В логах должно появиться `Registered tunnel connection`.

---

## Сценарий 3 — VPS с публичным IP

Подходит для постоянной работы сайта. Используется `docker-compose.yaml` (классическая схема: `nginx-proxy` + `certbot-dns-cloudflare`).

### 1. Подготовка DNS

В Cloudflare добавьте A-записи:

| Тип | Имя              | Значение            | Proxy    |
| --- | ---------------- | ------------------- | -------- |
| A   | `rapidstream.ru` | IP вашего сервера   | DNS only |
| A   | `www`            | IP вашего сервера   | DNS only |

> Включите Proxy (оранжевое облачко) **только после того, как certbot успешно получил сертификаты**.

### 2. Cloudflare API Token для DNS-01

1. Cloudflare Dashboard → **My Profile** → **API Tokens** → **Create Token** → **Edit zone DNS**.
2. Permissions: `Zone — DNS — Edit`. Zone Resources: `Include — Specific zone — rapidstream.ru`.
3. Положите токен в `certbot-dns/cloudflare.ini` (этот файл в `.gitignore`):

   ```ini
   dns_cloudflare_api_token = <ваш токен>
   ```

4. `chmod 600 certbot-dns/cloudflare.ini`.

### 3. Запуск

```bash
git clone https://github.com/<ваш-fork>/library-constructor.git
cd library-constructor

cp .env.example .env
mkdir -p storage/photos

docker compose up --build -d
docker compose logs -f certbot-dns
```

### 4. Автообновление сертификатов

```cron
0 3 * * * cd /path/to/library-constructor && docker compose run --rm certbot-dns certbot renew --quiet && docker compose restart nginx-proxy
```

---

## Проверка работоспособности

```bash
docker compose ps                     # все контейнеры running/healthy
docker compose logs backend           # стартовые логи бэка
docker compose logs frontend          # стартовые логи фронта
```

Frontend должен отдавать HTML, backend — отвечать на `/v2/`.

## Частые проблемы

- **CORS ошибка в браузере (Codespaces).** Убедитесь, что порт 8000 (backend) выставлен `Public` в Codespaces, иначе браузер не сможет добавить cookie/CORS-заголовки.
- **502 от Cloudflare Tunnel.** В Public Hostname нужно указывать имя контейнера (`http://frontend:80`), а не `localhost`.
- **MySQL не стартует / ошибка авторизации.** При смене паролей в `.env` старый volume становится несовместим. Очистка: `docker compose down -v` (стирает данные).
- **Codespace пересоздан, фронт ведёт на старый URL.** Имя Codespace зашито в бандл при сборке. Решение: `docker compose -f docker-compose.codespaces.yaml up --build -d`.
- **Rate limit Let's Encrypt.** Используйте `--staging` в команде certbot для тестов.
