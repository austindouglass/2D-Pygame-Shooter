#Created By: Austin Douglass
# Date: 7/7/19

# File: audio.py
# Note: Audio for gameplay events + music

#format: playSound('data\\sounds\\')

import pygame, random

SOUND_VOL = .5
MUSIC_VOL = .2
SONG_END = pygame.USEREVENT + 3

def playSound(filename : str):
#plays sound
    freeChannel = pygame.mixer.find_channel()
    
    if freeChannel is not None:
        freeChannel.set_volume(SOUND_VOL)
        freeChannel.play(pygame.mixer.Sound(filename))
    else:
        print("~ audio.py: No Free Channel Found")

def playerDeath():
    playSound('data\\sounds\\sfx_sounds_negative1.wav')

def playerHurt():
    playSound('data\\sounds\\sfx_sounds_impact5.wav')

def deadEnemy():
    playSound('data\\sounds\\sfx_coin_double1.wav')

def enemyHurt():
    playSound('data\\sounds\\sfx_sounds_impact11.wav')

def startPause():
    pygame.mixer.pause()
    pygame.mixer.music.pause()
    playSound('data\\sounds\\sfx_sounds_pause3_in.wav')

def endPause():
    playSound('data\\sounds\\sfx_sounds_pause3_out.wav')
    pygame.mixer.unpause()
    pygame.mixer.music.unpause()

def gameWon():
    playSound('data\\sounds\\sfx_coin_cluster4.wav')

def lvlSelect():
    playSound('data\\sounds\\jump-c-09 by cabled_mess.wav')

def chooseSounds( playerLostHealth : bool, killedEnemy : bool, enemiesHurt : bool):
#chooses sounds to play based on game info
    if playerLostHealth:
        playerHurt()
    if killedEnemy:
        deadEnemy()
    if enemiesHurt:
        enemyHurt()
        
##    if enemiesHurt > 2:
##        emeiesHurt = 2
##    
##    for e in range(enemiesHurt):
##        enemyHurt()

def setup_music() -> 'pygame obj':
    pygame.mixer.music.set_endevent(SONG_END)
    return SONG_END

def playMusicChannel(filename : str):
#plays music from sound channel
    freeChannel = pygame.mixer.find_channel()
    
    if freeChannel is not None:
        freeChannel.set_volume(MUSIC_VOL)
        freeChannel.play(pygame.mixer.Sound(filename), 0, 180000, 3000)
    else:
        print("~ audio.py: No Free Channel Found")
        
def playMusic(filename : str):
#plays music from pygame music
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    
  

def get_all_music() -> list:
    all_music = [
        'data\\music\\BrandNameAudio\\BNA-RELAXING MUSIC.wav',
        'data\\music\\chiptunes\\Juhani Junkala [Retro Game Music Pack] Level 1.wav',
        'data\\music\\chiptunes\\Juhani Junkala [Retro Game Music Pack] Level 2.wav',
        'data\\music\\chiptunes\\Juhani Junkala [Retro Game Music Pack] Level 3.wav'
 #        'data\\music\\NesShooter\\Warp Jingle.wav',
 #        'data\\music\\NesShooter\\Map.wav'
        ]
    random.shuffle(all_music)
    print('Music Shuffled: ' + str(all_music))
    return all_music

def relaxMusic():
#Creator Music?
    playMusic('data\\music\\BrandNameAudio\\BNA-RELAXING MUSIC.wav')

def hypeMusic():
#battle music?
    playMusic('data\\music\\chiptunes\\Juhani Junkala [Retro Game Music Pack] Level 1.wav')

def randomMusic():
#testing for random functionality
    playMusic(get_all_music()[0])
    
class Music:
    def __init__(self):
    #initilalizes the music setup
        self.playlist = get_all_music()
        self.volume = .2
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.set_endevent(SONG_END)
        playMusic(self.playlist[0])
        
    def check_song(self):
        for event in pygame.event.get():
            if event.type == SONG_END:
                play_next_song(self)
        
    def song_ended(self) -> 'pygame userevent / SONG_END':
    #returns what's considered the endevent
        return SONG_END
        
    def play_next_song(self):
    #ended song is sent to the end of playlist while next song starts
        self.playlist = self.playlist[1:] + [self.playlist[0]]
        playMusic(self.playlist[0])

    def set_volume(self, v : float):
        self.volume = v
        pygame.mixer.music.set_volume(self.volume)
