"""
SERVER DI COLLEGAMENTO A TIKTOK LIVE (versione Python)
--------------------------------------------------------
Questo server si collega a una diretta TikTok in corso e inoltra
nome + testo di chi scrive in chat alla pagina HTML dell'overlay
(multichat-overlay-nokeys.html) tramite WebSocket. Non serve Node.js,
solo Python.

Nella pagina HTML, nel campo "Indirizzo WS TikTok" del pannello di
configurazione, lascia (o inserisci) ws://localhost:8080: l'overlay
si collegherà automaticamente a questo server insieme a Twitch/YouTube.

COME USARLO:

1) Assicurati di avere Python 3.8 o superiore installato.
   Verifica con:  python --version   (o python3 --version)

2) Installa le due librerie necessarie con pip:

      pip install TikTokLive websockets

   (su alcuni sistemi potresti dover usare "pip3" invece di "pip")

3) Modifica qui sotto la riga con "NOME_UTENTE_TIKTOK" mettendo lo
   username TikTok (senza @) di chi sta facendo la diretta in quel
   momento — la diretta deve essere ATTIVA per potersi collegare.

4) Avvia il server:

      python server_tiktok.py

   Se tutto va bene vedrai nel terminale i messaggi di connessione
   e, mentre la diretta prosegue, ogni commento che arriva in chat.

5) Apri la pagina HTML dei pupazzetti nel browser (o in OBS come
   Browser Source). Nel campo "Indirizzo server WebSocket" lascia
   ws://localhost:8080 e premi "Connetti a TikTok".

NOTE IMPORTANTI:
- "TikTokLive" è una libreria open-source non ufficiale: si collega
  fingendosi uno spettatore della diretta, esattamente come farebbe
  un browser normale. Non esiste un'API pubblica ufficiale di TikTok
  per questo scopo.
- Funziona solo mentre la diretta è ATTIVA in quel momento.
- Se TikTok cambia qualcosa nella sua piattaforma, la libreria potrebbe
  smettere di funzionare finché non viene aggiornata: in tal caso prova
  ad aggiornarla con "pip install --upgrade TikTokLive".
"""

import asyncio
import json
import sys

# Forza l'output del terminale in UTF-8: su Windows, il Prompt dei comandi
# usa spesso una codifica (es. cp850) che NON supporta le emoji usate nei
# print() di questo script. Senza questa riga, quando arriva un vero
# commento/connessione da stampare, Python può lanciare un errore di
# codifica dentro un task in background e il programma si chiude di
# colpo senza mostrare nulla. Questa riga risolve il problema alla radice.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent, CommentEvent, DisconnectEvent
import websockets

# 1) Metti qui lo username TikTok della diretta (senza la @)
NOME_UTENTE_TIKTOK = "multiverso.animat"

# insieme delle pagine HTML attualmente collegate via WebSocket
client_collegati = set()

# client TikTokLive: si occupa del collegamento alla diretta
client = TikTokLiveClient(unique_id="@" + NOME_UTENTE_TIKTOK)


async def invia_a_tutti_i_client(nome: str, testo: str = ""):
    """Manda nome (e testo del commento) a tutte le pagine HTML collegate in questo momento."""
    if not client_collegati:
        return
    payload = json.dumps({"nome": nome, "testo": testo})
    invii = [ws.send(payload) for ws in list(client_collegati)]
    await asyncio.gather(*invii, return_exceptions=True)


@client.on(ConnectEvent)
async def su_connessione(event: ConnectEvent):
    print(f"🎥 Collegato alla diretta di @{event.unique_id} (room id: {client.room_id})")


@client.on(DisconnectEvent)
async def su_disconnessione(event: DisconnectEvent):
    print("⚠️  Disconnesso dalla diretta TikTok.")


@client.on(CommentEvent)
async def su_commento(event: CommentEvent):
    try:
        nome = event.user.nickname or event.user.unique_id or "Anonimo"
        print(f"💬 {nome}: {event.comment}")
        await invia_a_tutti_i_client(nome, event.comment)
    except Exception as errore:
        # Se qualcosa va storto nella gestione di un singolo commento,
        # lo stampiamo invece di lasciare che sparisca senza traccia.
        print("⚠️  Errore nella gestione di un commento:", errore)


async def gestisci_pagina_html(websocket):
    """Chiamata ogni volta che una pagina HTML si collega al server WebSocket."""
    client_collegati.add(websocket)
    print("🔗 Pagina HTML collegata.")
    try:
        async for _ in websocket:
            pass  # non ci aspettiamo messaggi dalla pagina, solo invii verso di lei
    finally:
        client_collegati.discard(websocket)
        print("🔌 Pagina HTML disconnessa.")


def su_errore_non_gestito(loop, contesto):
    """Chiamata da asyncio ogni volta che un errore 'silenzioso' avviene
    in un task in background (es. dentro la libreria TikTokLive)."""
    messaggio = contesto.get("exception", contesto.get("message"))
    print("💥 Errore interno non gestito:", messaggio)


async def main():
    asyncio.get_event_loop().set_exception_handler(su_errore_non_gestito)

    server_ws = await websockets.serve(gestisci_pagina_html, "localhost", 8080)
    print("✅ Server WebSocket avviato su ws://localhost:8080")

    try:
        # client.start() è NON bloccante: avvia la connessione e restituisce
        # subito un "task" in background, senza aspettare la fine della diretta.
        # Per questo il programma sembrava chiudersi da solo: dobbiamo aspettare
        # esplicitamente quel task, che resta attivo finché siamo connessi.
        task_connessione = await client.start()
        await task_connessione
    except Exception as errore:
        print("❌ Errore di collegamento alla diretta TikTok:", errore)
        print("Controlla che lo username sia corretto e che la diretta sia ATTIVA in questo momento.")
    finally:
        server_ws.close()
        await server_ws.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())
