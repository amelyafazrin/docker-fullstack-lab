# Docker Fullstack Lab

Project fullstack sederhana menggunakan Docker Compose dengan backend Python dan frontend Nginx.

## Arsitektur

- Backend: Python HTTP API.
- Frontend: Nginx.
- Container orchestration: Docker Compose.
- Persistent storage: Docker named volume.

## Menjalankan Aplikasi

Build dan jalankan seluruh service:

```bash
docker compose up -d --build
```

Periksa status container:

```bash
docker compose ps
```

## Akses Aplikasi

- Frontend: http://localhost:8080
- Backend API: http://localhost:8081/

## Menghentikan Aplikasi

```bash
docker compose down
```

Data backend disimpan menggunakan Docker named volume agar dapat bertahan ketika container dihentikan dan dijalankan kembali.

Webhook CI/CD Test - 3 November 2026
