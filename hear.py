import audioop
import pyaudio
import pyrebase
import os
from datetime import datetime
from time import sleep

def initFirebase(config, user_credentials):
    firebase = pyrebase.initialize_app(config)

    # Get a reference to the auth service
    auth = firebase.auth()

    # Get a reference to the database service
    db = firebase.database()

    user = auth.sign_in_with_email_and_password(user_credentials["email"], user_credentials["pass"])

    return auth, db, user 


def triggerWrite(auth, user, db):
    user = auth.refresh(user['refreshToken'])
    db.child("Alerta").child("Campainha").update({"mensagem": "Tem alguem na sua porta!", "date": str(datetime.now())})


#def monitorAudio(config, user):

def print_logo():
    print("\n\n\n\
    -------------------------------------------\n\
    |     ______  ___      ____ _  __   ___   |\n\
    |    / ____/ /   |    /  _/| |/ /  /   |  |\n\
    |   / /     / /| |    / /  |   /  / /| |  |\n\
    |  / /____ / ___ |_ _/ /_ /   |_ / ___ |_ |\n\
    |  \____(_)_/  |_(_)___(_)_/|_(_)_/  |_(_)|\n\
    -------------------------------------------\n\
    \n\n\n\
    ")                                            


def main():

    # Audio capture and trigger implementation as suggested at
    # https://stackoverflow.com/questions/2668442/detect-and-record-a-sound-with-python
    CHUNK = 1024
    THRESHOLD = 900

    audio_config = {
      "chunk": CHUNK,
      "threshold": THRESHOLD
    }

    # Firebase Config

    API_KEY = os.environ['API_KEY']
    AUTH_DOMAIN = os.environ['AUTH_DOMAIN']
    DATABASE = os.environ['DATABASE']
    PROJECT = os.environ['PROJECT']
    STORAGE = os.environ['STORAGE']

    user_credentials ={
            "email":  os.environ['CAIXA_EMAIL'],
            "pass": os.environ['CAIXA_PWD']
    }


    firebase_config = {
      "apiKey": API_KEY,
      "authDomain": AUTH_DOMAIN,
      "databaseURL": DATABASE,
      "projectId": PROJECT,
      "storageBucket": STORAGE
    }

    auth,db,user = initFirebase(firebase_config, user_credentials)

    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=audio_config["chunk"])

    print_logo()
    print('Listening...')
    count_noise = 0
    while True:
        data = stream.read(audio_config["chunk"], exception_on_overflow = False)

        if audioop.rms(data, 2) > audio_config["threshold"]:
            print('NOISE!')
            print(audioop.rms(data, 2))
            count_noise +=1
            if count_noise == 2:
                print("Audio detected!")
                triggerWrite(auth, user, db)
                count_noise = 0
                sleep(2)
            print('Listening...')
            sleep(0.1)
        else:
            count_noise = 0


if __name__ == '__main__':
    main()
