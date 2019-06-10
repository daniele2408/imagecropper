# imagecropper

Gli script presuppongono un db mysql attivo, l'indirizzo può essere settato nel config.yaml.

## Descrizione file

* database.py: inizializza il db, **droppa** eventuali tabelle già presenti, le crea di nuovo inserendo due utenti nella tabella user.
* tagginator.py: funzioni del back-end per restituire crop+id e per inserire tag di utenti nuovi o meno e aggiorna il db di conseguenza.
* db_funcs.py, utils_func.py: funzioni di appoggio
* testing_app.py: script di unit test