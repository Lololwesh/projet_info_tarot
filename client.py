import socket
import threading
import pickle

import joueur

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
SERVER = '192.168.0.44'
ADDR = (SERVER, PORT)



client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

main_joueur = joueur.Joueur()

def send(msg):
    message = pickle.dumps(msg)
    client.send(message)


def handle_server():
    while True:
        msg = pickle.loads(client.recv(2048))
        if msg == DISCONNECT_MESSAGE:
            print('[CLIENT] disconnecting...')
            break
        elif type(msg) != str:
            if msg[0] == 'SERVER':
                if msg[1] == 'message':
                    print(msg[2])
                elif msg[1] == 'action':
                    threading.Thread(target=eval(msg[2]), args=(msg[3:] if len(msg)>3 else [])).start()
            if msg[0] == 'LOBBY':
                if msg[1] == "action":
                    threading.Thread(target=eval(msg[2]), args=(msg[3:] if len(msg)>3 else [])).start()
                elif msg[1] == "message":
                    print(f"[LOBBY] {msg[2]}")
        else:
            print(msg)


def choisir_lobby(lst_lobbies):
    possible_lobbies = []
    for lobby in lst_lobbies:
        if lobby[0].count('/')<4:
            print(lobby[0])
            possible_lobbies.append(str(lobby[1]))
    print(f"taper + pour un nouveau lobby")
    lobby = input('Quel lobby ? ')
    while lobby != '+' and not lobby in possible_lobbies:
        lobby = input("Vous avez rentré un mauvais lobby\nQuel lobby choisissez vous ? ")
    if lobby != '+':
        lobby = int(lobby)
    client.send(pickle.dumps(("SERVER", "action", "choisir_lobby", lobby)))

def recevoir_jeu(main):
    main_joueur.main=main
    print(f"J'ai reçu un jeu: {main}")

def verifier_reception_jeu():
    if main_joueur.main == []:
        send(("LOBBY", "action", "jeu_pas_recu"))

def choisir_prise():
    print('taper:\n 1 pour passer\n2 pour faire une petite\n3 pour faire une garde\n4 pour faire une garde-sans\n5 pour faire une garde-contre')
    prise = input()
    prise = ['passe', 'petite', 'garde', 'garde-sans', 'garde-contre'][int(prise)-1]
    send(('LOBBY', 'action', 'recevoir_prise', prise))

def username_est_valide(username):
    for charactere in username:
        if not (charactere.isalnum() or charactere in '-_'):
            return False
    return True

username = input('Pseudonyme: ')

while not username_est_valide(username):
    username = input("\nLe pseudonyme donné n'est pas valide\n\nPseudonyme: ")


client.connect(ADDR)
send(username)

server_thread = threading.Thread(target=handle_server)

server_thread.start()

