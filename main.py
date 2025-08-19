import pygame
import pygame.midi
import threading
import time
from mido import MidiFile, tick2second
import random

mid = MidiFile('PinkPanther.midi', clip=True)

# Initialiser Pygame et MIDI
pygame.init()
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
WINDOW = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
BACKGROUND = (0, 0, 0)

# Dessin des rectangles
RECT_INFO = None # sera un dict aec 'rect','color','end_time'
RECT_LOCK = threading.Lock() # éviter les conflits

pygame.midi.init()
player = pygame.midi.Output(0)
player.set_instrument(0)

# Variables entre midi / pygame
running = True
time_to_wait = 0

# Fonction pour afficher rectangle
def show_rectangle(position, size=(50, 50), color=(255, 0, 0), duration=0.5):
    global RECT_INFO
    end_time = time.time() + duration
    with RECT_LOCK:
        RECT_INFO = {'rect': pygame.Rect(position, size), 'color': color, 'end_time': end_time}

# Fonction pour jouer le MIDI dans un thread
def play_midi():
    tempo = 500000  # valeur par défaut
    for track in mid.tracks:
        for msg in track:
            if (running):
                time.sleep(tick2second(msg.time, mid.ticks_per_beat, tempo))
                if msg.type == 'note_on':
                    player.note_on(msg.note, msg.velocity)
                    show_rectangle(position=(random.random() * WINDOW_WIDTH, random.random() * WINDOW_HEIGHT))  # exemple de position
                elif msg.type == 'note_off':
                    player.note_off(msg.note, msg.velocity)
                elif msg.type == 'set_tempo':
                    tempo = msg.tempo

# Lancer le thread 
midi_thread = threading.Thread(target=play_midi)
midi_thread.start()

# Boucle principale Pygame
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            midi_thread()

    WINDOW.fill(BACKGROUND)
    # dessiner

    # Dessiner le rectangle si actif
    with RECT_LOCK:
        if RECT_INFO and time.time() < RECT_INFO['end_time']:
            pygame.draw.rect(WINDOW, RECT_INFO['color'], RECT_INFO['rect'])
        else:
            RECT_INFO = None  # effacer le rectangle quand le temps est écoulé


    pygame.display.update()

# Fin
midi_thread.join()  # attendre que le thread MIDI finisse
player.close()
pygame.midi.quit()
pygame.quit()

pygame.draw.rect