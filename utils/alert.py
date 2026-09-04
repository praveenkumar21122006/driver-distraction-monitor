from pathlib import Path

import pygame


class AlertSystem:

    def __init__(self, sound_file=None):

        self.sound = None
        self.channel = None
        project_root = Path(__file__).resolve().parents[1]

        if sound_file is None:
            sound_file = project_root / "assets" / "alarm.wav"
        else:
            sound_file = Path(sound_file)
            if not sound_file.is_absolute():
                sound_file = project_root / sound_file

        try:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(2)

            if sound_file.exists():
                self.sound = pygame.mixer.Sound(str(sound_file))
                self.sound.set_volume(1.0)
                self.channel = pygame.mixer.find_channel(True)

        except Exception:
            self.sound = None
            self.channel = None

    def beep(self):

        if self.sound is None:
            return

        try:
            if self.channel is None:
                self.channel = pygame.mixer.find_channel(True)

            if self.channel and not self.channel.get_busy():
                self.channel.play(self.sound, loops=-1)
        except Exception:
            try:
                self.sound.play(loops=-1)
            except Exception:
                pass

    def stop(self):

        if self.sound:
            try:
                self.sound.stop()
            except Exception:
                pass

        if self.channel:
            try:
                self.channel.stop()
            except Exception:
                pass