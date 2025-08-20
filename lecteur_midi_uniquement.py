import pygame.midi
import time
from mido import MidiFile, tick2second

mid = MidiFile('PinkPanther.midi', clip=True)

# Initialiser Pygame MIDI
pygame.midi.init()
player = pygame.midi.Output(0)

# Variables entre midi / pygame
time_to_wait = 0
total_time = 0
for track in mid.tracks:
    total_time += sum(l.time for l in track)

# Jouer midi
# L'appli devra jouer toutes les tracks disponibles en même temps
# Pour le faire, j'ai une liste avec le temps en ticks à attendre pour le prochain instrument

tempo = 500000  # valeur par défaut
player.set_instrument(56, 2) # canal 2 => trompette
player.set_instrument(0, 11) # canal 11 => piano

index_list = []
wait_ticks_list = []

# first run
for track in mid.tracks:
    index_list.append(0)
    wait_ticks_list.append(track[0].time)

while True:
    min_time = min(wait_ticks_list)
    #tempo non défini au début (chaque temps d'attente est 0 jusqu'à définition du tempo donc aucun souci)
    time.sleep(tick2second(min_time, mid.ticks_per_beat, tempo))
    wait_ticks_list = [x - min_time for x in wait_ticks_list]
    
    for i in range(len(wait_ticks_list)):
        if wait_ticks_list[i] == 0:
            msg = mid.tracks[i][index_list[i]]
            match msg.type:
                case 'note_on':
                    player.note_on(msg.note, msg.velocity, msg.channel)
                case 'note_off':
                    player.note_off(msg.note, msg.velocity, msg.channel)
                case 'set_tempo':
                    tempo = msg.tempo
                case 'control_change':
                    player.write_short(0xB0 + msg.channel, msg.control, msg.value)
                case 'pitchwheel':
                    lsb = msg.pitch & 0x7F
                    msb = (msg.pitch >> 7) & 0x7F
                    player.write_short(0xE0 + msg.channel, lsb, msb)
                case _:
                    print(msg)
            wait_ticks_list[i] = mid.tracks[i][index_list[i] + 1].time
            index_list[i] += 1
            if (mid.tracks[i][index_list[i]].type == 'end_of_track'):
                index_list.remove(index_list[i])
                wait_ticks_list.remove(wait_ticks_list[i])
    if (len(index_list) == 0):
        exit(0)

pygame.midi.quit()