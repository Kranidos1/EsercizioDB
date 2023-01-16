import subprocess
import dropbox
import dropbox.files 
import os
import requests
import time


#from Database.ConnectionDAO import ConnectionDAO


'''
const dbx = new Dropbox({ 
  clientId: '<APP_KEY>',
  clientSecret: process.env.DBX_CLIENT_SECRET,
  refreshToken: process.env.DBX_REFRESH_TOKEN
});
'''

#TODO: MECCANISMO A SEMAFORO ,ACCESS_TOKEN AUTOMATICO
#https://www.dropbox.com/home/Applicazioni/TestingTia-

#https://dropbox-sdk-python.readthedocs.io/en/latest/api/dropbox.html
#per key https://www.dropbox.com/developers/apps


#In dropbox api ,sezione App console ,ti fa creare un app fornendoti app_key e app_secret. Questa app e' legata a una cartella a cui un utente non può accedere in maniera automatica :
# deve raggiungere un link fornito dal developer ,effettuare il login con un account dropbox ,accettare la connessione alla folder ,inserire il codice di accesso manualmente nell'App che si occupa delle dump e da qui in poi fare richieste.
#Questo e' l'OAuthFlow imposto da dropbox ogni volta che un utente deve caricare la dump del database .Ciò non permetterebbe un automazione del processo di inserimento.
#Tuttavia ,durante la configurazione ,si può effettuare OAuthFlow ,prendere il codice di accesso, generare un refresh token che e' eterno e salvarlo nel database delle configurazioni.
#Il refresh token permette di fare delle call evitando l'OAuthFlow.

#access token ormai scaduto
#xhoLZS4jW2gAAAAAAAAAGa0b9CXeUaqUrd5ws9gvmf8

#soluzione tokens
#https://www.codemzy.com/blog/dropbox-long-lived-access-refresh-token

#chiamata con access token per ottenere refresh token infinito e evitare all'utente OAuth flow ,automatizzando il processo (ora genera errore in quanto access token scaduto)
#r = requests.post(url="https://api.dropboxapi.com/oauth2/token" ,params={"client_id":"hu9v12z463b5ms9" ,"client_secret":"bl44dk2wwgctk2y" ,"code":"xhoLZS4jW2gAAAAAAAAAGt-i0_W91IZPo5ajs0zaMys" ,"grant_type":"authorization_code"})
#print(r.content)

#refresh token tutt'ora utilizzato (ottenuto il 15/01/2023)
#"bP29Rbo9008AAAAAAAAAAan3hx-H-JIvEXg2rEmuyaT3Yv8cEij8seV0owoEf8zm"

def sendFile():

    chunk_size = 1024*1024
    dbx = dropbox.Dropbox(app_key="hu9v12z463b5ms9" ,app_secret="bl44dk2wwgctk2y" ,oauth2_refresh_token="bP29Rbo9008AAAAAAAAAAan3hx-H-JIvEXg2rEmuyaT3Yv8cEij8seV0owoEf8zm")
    
    file_path = "db_dump.sql"
    
    f = open(file_path ,"rb")
    file_size = os.path.getsize(file_path)
    
    #crea sessione di upload da 0
    upload_session_start_result = dbx.files_upload_session_start(f.read(0))

    #oggetto per upload
    cursor = dropbox.files.UploadSessionCursor(session_id=upload_session_start_result.session_id,offset=f.tell())
    
    #carica file nella folder corrente dell'app :  Applicazioni/TestingTia-/testing.sql
    commit = dropbox.files.CommitInfo(path="/testing.sql" ,mode=dropbox.files.WriteMode.overwrite)
    
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

    #crea il file di log
    log_file = open('zip_log.txt', 'w')
    
    try:
        # Comprime un file .sql in un file zip utilizzando 7-Zip
        # a = crea o aggiungi
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
    
    #da nascondere
    db_name = ''
    db_user = ''
    db_pass = ''


    #creare il file di log
    log_file = open('dump_log.txt', 'w')

    # eseguire la dump del database
    try:
        
        subprocess.run(['mysqldump', '-u' + db_user, '-p' + db_pass, db_name], 
                    stdout=open('db_dump.sql', 'w'), stderr=log_file)
        
        #controlla se file creato ha una grandezza maggiore di 0
        if os.path.getsize("db_dump.sql") > 0 :
            fileCheck = 1
        else:
            #il file ha una grandezza 0 quindi viene cancellato
            os.remove("db_dump.sql")
            
            
    except Exception as e:
        #se errore viene scritto in dump_log.txt e fileCheck rimane 0 ,non procedendo (a meno che l'errore non sia per l'utilizzo poco sicuro della password in linea di comando)
        print(str(e))
        log_file.write(str(e))
        log_file.close()

    log_file.close()
    
    
    if fileCheck == 1:
        #passa alla funzione zip
        to7Zip()
    
    
        

