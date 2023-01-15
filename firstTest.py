import subprocess
import dropbox
import os
import requests
import time
import json

#lettura file e controllo check evitando commenti

#from Database.ConnectionDAO import ConnectionDAO
#l'idea e' quella di aprire una download bar che di default non si puo chiudere. Tuttavia ,se dovesse mancare internet ,
#viene data la possibilità di chiuderla e prima di chiudersi salva in un file di log che manca internet.

#xhoLZS4jW2gAAAAAAAAAGa0b9CXeUaqUrd5ws9gvmf8
#soluzione tokens
#https://www.codemzy.com/blog/dropbox-long-lived-access-refresh-token

r = requests.post(url="https://api.dropboxapi.com/oauth2/token" ,params={"client_id":"hu9v12z463b5ms9" ,"client_secret":"bl44dk2wwgctk2y" ,"code":"xhoLZS4jW2gAAAAAAAAAGt-i0_W91IZPo5ajs0zaMys" ,"grant_type":"authorization_code"})
print(r.content)

#"bP29Rbo9008AAAAAAAAAAan3hx-H-JIvEXg2rEmuyaT3Yv8cEij8seV0owoEf8zm"

'''
const dbx = new Dropbox({ 
  clientId: '<APP_KEY>',
  clientSecret: process.env.DBX_CLIENT_SECRET,
  refreshToken: process.env.DBX_REFRESH_TOKEN
});
'''
#SEGUI LA GUIDA ,REFRESH TOKEN ETERNO
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

#TODO: MECCANISMO A SEMAFORO ,ACCESS_TOKEN AUTOMATICO
#https://www.dropbox.com/home/Applicazioni/TestingTia-

#https://dropbox-sdk-python.readthedocs.io/en/latest/api/dropbox.html
#per key https://www.dropbox.com/developers/apps

def sendFile():

    chunk_size = 1024*1024
    dbx = dropbox.Dropbox("sl.BW-DIq4C-HWOJZ9ZlB_r7Yx46tCM7baOFrxhb61XmuoM5lJLxsI40aN_rPNDUfkToIg_TV4gFKNqaueMSKruEM23WBS93_aMX5pl1ZbsxFdplWcEejT3t0olS0wvbvhmbLGs_msC9GFN")
    
    file_path = "db_dump.sql"
    
    f = open(file_path ,"rb")
    file_size = os.path.getsize(file_path)
    
    #crea sessione da 0
    upload_session_start_result = dbx.files_upload_session_start(f.read(0))

    #oggetto per upload
    cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,offset=f.tell())
    
    #carica file nell app corrente sottoforma di testing.sql
    commit = dropbox.files.CommitInfo(path="/testing.txt")
    
    while f.tell() < file_size:
        
        try:
            response = requests.get("http://www.google.com", timeout=10)
        except requests.ConnectionError:
            print("Connessione interrotta. Riprendere il caricamento...")
            time.sleep(15)
        except requests.ReadTimeout :
            print("Connessione interrotta. Riprendere il caricamento...")
            time.sleep(15)
            #with open("offset.txt", "w") as f:
                #f.write(str(offset))
        else:
            
            #verifica se il chunk corrente e' l'ultimo
            if ((file_size - f.tell()) <= chunk_size):
                #se non viene chiusa chunk persi. Possibile sfruttare su perdita connessione
                print(dbx.files_upload_session_finish(f.read(chunk_size),cursor,commit))
            else:
                #carica il chunk corrente e aggiorna la posizione del cursore per il prossimo chunk
                dbx.files_upload_session_append(f.read(chunk_size),cursor.session_id,cursor.offset)
                
                cursor.offset = f.tell()
     
def to7Zip():

    #creare il file di log
    log_file = open('zip_log.txt', 'w')
    
    try:
        # Comprimere un file .sql in un file zip utilizzando 7-Zip
        #spiegazione lista : 7z comando  ,a argomento e significa crea o aggiungi ad archivio esistente 
        subprocess.run(['7z', 'a', 'dumb_db.zip', 'db_dump.sql'] ,stderr=log_file)
    
        
    except Exception as e:
        #se errore viene scritto in dump_log.txt
        log_file.write(str(e))
        log_file.close()

    log_file.close()

    check = True
    while(check):
        try:
            response = requests.get("http://www.google.com", timeout=10)
        except requests.ConnectionError:
            print("Connessione interrotta. Riprendere il caricamento...")
            time.sleep(15)
        except requests.ReadTimeout :
            print("Connessione interrotta. Riprendere il caricamento...")
            time.sleep(15)
        else:
            check = False
            sendFile() 

 
def createDump():
    
    fileCheck = 0 
    
    db_name = 'database_notifica'
    db_user = 'root'
    db_pass = 'Dante200-'

    #creare il file di log
    log_file = open('DumpHandler/dump_log.txt', 'w')

    # eseguire la dump del database
    try:
        
        subprocess.run(['mysqldump', '-u' + db_user, '-p' + db_pass, db_name], 
                    stdout=open('db_dump.sql', 'w'), stderr=log_file)
        
        #controlla se file creato ha una grandezza maggiore di 0
        if os.path.getsize("db_dump.sql") > 0 :
            fileCheck = 1
            
            
    except Exception as e:
        #se errore viene scritto in dump_log.txt
        print(str(e))
        log_file.write(str(e))
        log_file.close()

    log_file.close()
    
    #TODO check su filelog
    if fileCheck == 1:
        to7Zip()
    
    
        
createDump()
