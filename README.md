# tv_autobook
Tool zum automatischen Buchen von Zahlungseingängen des Technologenverbandes

## Benötigte Software

- [Python](https://www.python.org/downloads/), any version beyond 3.8 should do it
- [sqlite3](https://sqlite.org/download.html)

Lade dieses Repo in den gewünschten Ordner und erstelle ein Virtual Environment. Installiere die Dependencies (nur pandas) mit

```bash
pip install -r requirements.txt
```

Starte das Programm mit 

```bash
python autobook.py <path/to/sql/file> <fee>
```
