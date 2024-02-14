from __future__ import annotations
from pygame import mixer
from settings import *

class Audio:
    _audio = None # Audio singleton. Use instance() to access it.
    def __init__(self) -> None:
        mixer.set_num_channels(20)
        mixer.set_reserved(4)
        self.reserv_channel0 = mixer.Channel(0)
        self.reserv_channel1 = mixer.Channel(1)
        self.reserv_channel2 = mixer.Channel(2)
        self.reserv_channel3 = mixer.Channel(2)
        mixer.music.load(BG_MUSIC_PATH)
        mixer.music.set_volume(BG_MUSIC_VOL)
        self.click = mixer.Sound(CLICK_SOUND_PATH)
        self.click.set_volume(SFX_VOL)
        self.game_cleared = mixer.Sound(GAME_CLEARED_SOUND_PATH)
        self.game_cleared.set_volume(SFX_VOL)
        self.bullet0 = mixer.Sound(BULLET0_SOUND_PATH)
        self.bullet0.set_volume(SFX_VOL)
        self.bullet1 = mixer.Sound(BULLET1_SOUND_PATH)
        self.bullet1.set_volume(SFX_VOL)
        self.bullet2 = mixer.Sound(BULLET2_SOUND_PATH)
        self.bullet2.set_volume(SFX_VOL)
        self.player_hit = mixer.Sound(PLAYER_HIT_SOUND_PATH)
        self.player_hit.set_volume(SFX_VOL)
        self.player_death = mixer.Sound(PLAYER_DEATH_SOUND_PATH)
        self.player_death.set_volume(SFX_VOL)
        self.extra_score = mixer.Sound(EXTRA_SCORE_SOUND_PATH)
        self.extra_score.set_volume(SFX_VOL)
        self.power_up = mixer.Sound(POWER_UP_SOUND_PATH)
        self.power_up.set_volume(SFX_VOL)
        self.parasite_bullet = mixer.Sound(PARASITE_BULLET_SOUND_PATH)
        self.parasite_bullet.set_volume(SFX_VOL)
        self.flooder_bullet = mixer.Sound(FLOODER_BULLET_SOUND_PATH)
        self.flooder_bullet.set_volume(SFX_VOL)
        self.gear_bullet = mixer.Sound(GEAR_BULLET_SOUND_PATH)
        self.gear_bullet.set_volume(SFX_VOL)
        self.beast_bullet = mixer.Sound(BEAST_BULLET_SOUND_PATH)
        self.beast_bullet.set_volume(SFX_VOL)
        self.enemy_death = mixer.Sound(ENEMY_DEATH_SOUND_PATH)
        self.enemy_death.set_volume(SFX_VOL)

    @staticmethod
    def instance() -> Audio:
        if not Audio._audio:
            Audio._audio = Audio()
        return Audio._audio
    
    def play_bg_music(self):
        mixer.music.play(-1)

    def stop_bg_music(self):
        mixer.music.stop()

    def play_click_sound(self):
        self.click.play()

    def play_game_cleared_sound(self):
        self.game_cleared.play()
    
    def play_player_bullet_sound(self, bullet_level):
        sound = None
        if bullet_level == 0:
            sound = self.bullet0
        elif bullet_level == 1:
            sound = self.bullet1
        elif bullet_level == 2:
            sound = self.bullet2
        sound.play()

    def play_player_hit_sound(self):
        self.player_hit.play()

    def play_player_death_sound(self):
        self.player_death.play()

    def play_extra_score_sound(self):
        self.extra_score.play()

    def play_power_up_sound(self):
        self.power_up.play()

    def play_enemy_bullet_sound(self, enemy_type):
        if enemy_type == ENEMY_TYPE_PARASITE:
            self.reserv_channel1.play(self.parasite_bullet)
        elif enemy_type == ENEMY_TYPE_FLOODER_DOWN:
            self.reserv_channel2.play(self.flooder_bullet)
        elif enemy_type == ENEMY_TYPE_GEAR:
            self.gear_bullet.play()
        elif enemy_type == ENEMY_TYPE_BEAST:
            self.reserv_channel3.play(self.beast_bullet)
        else:
            raise RuntimeError(f"Invalid type for enemy bullet sound: {enemy_type}")

    def play_enemy_death_sound(self):
        self.reserv_channel0.play(self.enemy_death)
