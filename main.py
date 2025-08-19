from mido import MidiFile, tick2second
import pygame
import pygame.midi
import time

mid = MidiFile('PinkPanther.midi', clip=True)
pygame.midi.init()

tempo = 500000 # valeur par défaut qui sera changée lors de la lecture du fichier midi

player = pygame.midi.Output(0)
instrument = 0
player.set_instrument(instrument)

for track in mid.tracks:
    for line in track:
        time.sleep(tick2second(line.time, mid.ticks_per_beat, tempo))
        print(line)
        match (line.type):
            case "note_on":
                player.note_on(line.note, line.velocity)
            case "note_off":
                player.note_off(line.note, line.velocity)
            case "set_tempo":
                tempo = line.tempo