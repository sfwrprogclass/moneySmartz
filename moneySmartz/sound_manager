import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.current_music = None
        self.music_volume = 0.5
        
    def load_music(self, filename, name):
        """Load music file and store it by name"""
        # We don't actually load the file, we just store the path
        # Pygame mixer loads music when played
        self.sounds[name] = filename
        
    def play_music(self, name, loops=-1):
        """Play background music by name"""
        if name in self.sounds:
            if self.current_music != name:
                try:
                    pygame.mixer.music.load(self.sounds[name])
                    pygame.mixer.music.set_volume(self.music_volume)
                    pygame.mixer.music.play(loops)
                    self.current_music = name
                except Exception as e:
                    print(f"Error playing music: {e}")
                    
    def stop_music(self):
        """Stop currently playing music"""
        pygame.mixer.music.stop()
        self.current_music = None
        
    def set_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.music_volume)

