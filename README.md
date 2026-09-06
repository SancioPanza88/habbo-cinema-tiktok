# Habbo Cinema TikTok 🎬

Sala cinema in stile Habbo (`habbo_cinema_real.html`, ~2250 righe) con schermo video configurabile, editor collisioni integrato e **integrazione TikTok Live** via `server_tiktok.py` (WebSocket locale): gli spettatori entrano in sala come personaggi Habbo.

> 📌 **Stato reale: esperimento funzionante ma incompleto.** Il codice c'è e gira, mancano rifiniture, bilanciamento e pulizia. Pubblicato così com'è dalla cartella "da finire".

## Avvio

1. Metti l'URL del film (m3u8 o mp4) in `video_url.js`:
   ```js
   window.VIDEO_URL = "https://.../film.m3u8";
   ```
2. (Facoltativo, per gli spettatori TikTok) avvia il bridge:
   ```bash
   pip install TikTokLive websockets
   python server_tiktok.py
   ```
3. Apri `habbo_cinema_real.html` nel browser (o via `python -m http.server`).

Senza URL video lo schermo resta in attesa; senza server TikTok la sala funziona in locale.

## Contenuto

| File | Ruolo |
|---|---|
| `habbo_cinema_real.html` | sala, player, editor collisioni |
| `video_url.js` | URL del film (da compilare) |
| `collisioni.json` | mappa collisioni della sala |
| `server_tiktok.py` | bridge TikTok Live → WebSocket |
| `personaggi-habbo/` | sprite personaggi (rinominata da `personaggi habbo`, contenuto invariato) |

> ⚖️ Fan project non ufficiale, senza affiliazione con Habbo/Sulake o TikTok.

## Licenza

Nessuna licenza definita (progetto personale).
