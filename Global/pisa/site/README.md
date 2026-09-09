# PISA España 2000-2025 · pisa.victoriano.me

Contenido estático de https://pisa.victoriano.me (antes https://victoriano.me/pisa/): página de aterrizaje, manifiesto y metadatos del dataset PISA España 2000-2025, pensado para que una persona o un agente pueda empezar a analizarlo solo con la URL.

## Arquitectura

- **Dónde vive**: en el repo `victoriano/social-sciences-microdata`, carpeta `Global/pisa/site/` (este directorio), junto al pipeline que genera los datos (`Global/pisa/`).
- **Deploy automático**: cada push a `main` que toque esta carpeta dispara un despliegue de Cloudflare Pages (proyecto `pisa`, conectado al repo, root directory `Global/pisa/site`). Sin comando de build; el directorio de salida es la propia carpeta.
- **Dominio**: `pisa.victoriano.me` es el custom domain del proyecto Pages (el DNS se crea solo al asignarlo, porque la zona `victoriano.me` está en Cloudflare).
- **Los Parquet NO están en el repo**: pesan 11 MB y 160 MB y Pages limita a 25 MB por archivo. Viven en un bucket de Cloudflare R2 (`pisa-data`, egress gratis) servidos en `https://data.pisa.victoriano.me/<archivo>` (custom domain del bucket). Las URLs absolutas de `manifest.json` apuntan ahí.
- **Redirecciones del sitio antiguo** (Redirect Rules en la zona `victoriano.me`):
  - `/pisa/data/*` → `https://data.pisa.victoriano.me/*` (los enlaces de descarga ya publicados siguen funcionando)
  - `/pisa/*` → `https://pisa.victoriano.me/*` (el resto)

## Cómo actualizar

1. Edita lo que toque (`index.html`, `manifest.json`, `metadata/`...) dentro de `Global/pisa/site/` y haz push a `main` (o abre PR, como prefieras).
2. Cloudflare Pages despliega solo en aproximadamente un minuto. Comprueba https://pisa.victoriano.me/manifest.json al acabar.
3. Si cambias un archivo de `metadata/`, regenera su sha256 en `metadata_checksums` dentro de `manifest.json`:
   `shasum -a 256 metadata/<archivo>`
4. Si cambian los Parquet, súbelos al bucket R2 `pisa-data` (`npx wrangler r2 object put pisa-data/<archivo> --file=<archivo>`) y actualiza `bytes` y `sha256` en `manifest.json`.
