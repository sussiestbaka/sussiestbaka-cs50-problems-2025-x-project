from app import create_app, db
from dotenv import load_dotenv
import os


app = create_app()

with app.app_context():
    db.create_all()


if __name__ == '__main__':

    app.config['SESSION_COOKIE_HTTPONLY'] = True 
    app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
    app.config["FFE_BASE_DIRECTORY"] = '/home/khadas/AI/known_faces'
    load_dotenv()
    # print(os.getenv('SECRET_KEY'))
    app.run(host='0.0.0.0', port=5000)
    #os.run("nmcli d wifi hotspot ifname wlan1 ssid UAL_PROYECTO_MEC password UALMECATRONICA2025")
    
