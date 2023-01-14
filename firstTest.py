import subprocess
import dropbox
import os
import requests


#from Database.ConnectionDAO import ConnectionDAO

'''
conn = ConnectionDAO()


# creare cursore
cur = conn.connection.cursor()

# eseguire query
for i in range(1500 ,15000):
    print("ok")
    cur.execute("INSERT INTO `message` VALUES (%s,'2023-01-07 09:59:10','Mattia',0,'Test','2023-01-20 21:54:17',NULL,'1',NULL,0,NULL,'Testing','Ricorda Fatture',NULL,'[{\"obj\":\"testo\" ,\"label\":\"Testo\",\"id\":\"txt1\"},{\"obj\":\"testo\" ,\"label\":\"Testo\",\"id\":\"txt2\"}]','[{\"obj\":\"bottone\",\"label\":\"Ok\",\"function\":\"func.rispostaSemplice\",\"id\":\"bottonetmp1\"},{\"obj\":\"bottone\",\"label\":\"Rispondi\",\"function\":\"func.rispondi\",\"id\":\"bottonetmp2\"}]',NULL);",[i])

conn.connection.commit()
# recuperare i risultati
results = cur.fetchall()

# stampare i risultati
for row in results:
    print(row)

# chiudere cursore e connessione
cur.close()

conn.chiudiConnessione(conn.connection)
''' 

#https://dropbox-sdk-python.readthedocs.io/en/latest/api/dropbox.html
#per key https://www.dropbox.com/developers/apps
'''
def sendFile():
    # Creare una connessione Dropbox
    dbx = dropbox.Dropbox("sl.BW4c5fKrdPFENSUKIDBYdjuik7ZL5VKTBa1LL2BH6AvMHHpy_07aQRX31mmjqfgcPrDseeJ6jwOsnyQg4hCKkrdxzMWrNrIUzM-C5YjsI1fuM1EyGLCd7zYMH5Mhei4ARYZ0UotzDow5")

    # Aprire il file da caricare
    file = open("dump_log.txt", "rb")
    
    # Iniziare una sessione di caricamento
    #da fixare
    session = dbx.files_upload_session_start(file.read(1024*1024) )

    # Caricare il file in piccole parti
    #file position
    offset = file.tell()
    file_size = os.path.getsize("dump_log.txt")
    while offset < file_size:
        # Verificare la connessione
        try:
            response = requests.get("http://www.google.com", timeout=10)
        except requests.ConnectionError:
            print("Connessione interrotta. Riprendere il caricamento...")
            # Salva l'offset su un file di controllo o un db
            with open("offset.txt", "w") as f:
                f.write(str(offset))
        else:
            file.seek(offset)
            data = file.read(1024*1024)
            session = dbx.files_upload_session_append(data, session.session_id, offset)
            offset = file.tell()

    # Chiudere la sessione di caricamento e caricare il file su Dropbox
    response = dbx.files_upload_session_finish("/dump_log.txt", session.session_id, offset)
    print("File caricato con successo su Dropbox con ID: ", response.id)
'''

def sendFile():

    chunk_size = 1024*1024
    dbx = dropbox.Dropbox("sl.BW4c5fKrdPFENSUKIDBYdjuik7ZL5VKTBa1LL2BH6AvMHHpy_07aQRX31mmjqfgcPrDseeJ6jwOsnyQg4hCKkrdxzMWrNrIUzM-C5YjsI1fuM1EyGLCd7zYMH5Mhei4ARYZ0UotzDow5")
    
    file_path = "./DumpHandler/dump_log.txt"
    
    f = open(file_path ,"rb")
    file_size = os.path.getsize(file_path)
    
    upload_session_start_result = dbx.files_upload_session_start(f.read(0))

    cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,
                                               offset=f.tell())
    
    commit = dropbox.files.CommitInfo(path="/testing.txt")
    
    
    while f.tell() < file_size:
        
        if ((file_size - f.tell()) <= chunk_size):
            print(dbx.files_upload_session_finish(f.read(chunk_size),
                                            cursor,
                                            commit))
        else:
            dbx.files_upload_session_append(f.read(chunk_size),
                                            cursor.session_id,
                                            cursor.offset)
            cursor.offset = f.tell()
     
def to7Zip():

    #creare il file di log
    log_file = open('./DumpHandler/zip_log.txt', 'w')
    
    try:
        # Comprimere un file .sql in un file zip utilizzando 7-Zip
        #spiegazione lista : 7z comando  ,a argomento e significa crea o aggiungi ad archivio esistente 
        subprocess.run(['7z', 'a', './DumpHandler/dumb_db.zip', './DumpHandler/db_dump.sql'] ,stderr=log_file)
    
        
    except Exception as e:
        #se errore viene scritto in dump_log.txt
        log_file.write(str(e))
        log_file.close()

    log_file.close()
    
    sendFile() 

 
def createDump():
    
    db_name = 'database_notifica'
    db_user = 'root'
    db_pass = 'Dante200-'

    #creare il file di log
    log_file = open('DumpHandler/dump_log.txt', 'w')

    # eseguire la dump del database
    try:
        
        subprocess.run(['mysqldump', '-u' + db_user, '-p' + db_pass, db_name], 
                    stdout=open('./DumpHandler/db_dump.sql', 'w'), stderr=log_file)
        
    except Exception as e:
        #se errore viene scritto in dump_log.txt
        print(str(e))
        log_file.write(str(e))
        log_file.close()

    log_file.close()
    
    to7Zip()
    
    
        
createDump()
