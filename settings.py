from pygame import event

DEBUG = False

# GENERAL INFO
WIN_WIDTH = 640      # Window width
GAME_WIDTH = 540     # Game width
WIN_HEIGHT = 480     # Window height

WIN_ICON_PATH = "./assets/img/player.png"
GAME_TITLE = "Space Warrior"
GAME_SUBTITLE = "-- left-click to play --"
LEVEL_CLEARED_TEXT = "Level cleared"
GAME_OVER_TEXT = "GAME OVER"
GAME_OVER_SUBTITLE = "-- left-click to restart --"
GAME_CLEARED_TEXT = "GAME CLEARED"
GAME_CLEARED_SUBTITLE = "-- left-click to restart --"
FRAME_RATE = 60

TITLE_FONT_PATH = "./assets/font/Pixeltype.ttf"
TITLE_FONT_SIZE = 30
TITLE_COLOR = "white"

SUBTITLE_FONT_PATH = "./assets/font/Pixeltype.ttf"
SUBTITLE_FONT_SIZE = 25
SUBTITLE_COLOR = "grey"

STATS_FONT_PATH = "./assets/font/Pixeltype.ttf"
STATS_FONT_SIZE = 20
STATS_COLOR = "white"

# BACKGROUND
BG_BACK_PATH = "./assets/img/bg_space_back.png"
BG_FRONT_PATH = "./assets/img/bg_space_front.png"
BG_FRONT_SPEED = 0.2
BG_BACK_POS_RATIO = 0.5         # Between 0 & 1. Low values produces a strong parallax effect

# STATS
STATS_LEFT = 10
STATS_HEIGHT = 100
STATS_CENTERY = WIN_HEIGHT//2
STATS_LEN = 4                   # Number of stats to show

# GAME STATE
STATE_START = 0
STATE_PLAY = 1
STATE_LEVEL_CLEARED = 2
STATE_GAME_CLEARED = 3
STATE_GAME_OVER = 4

LEVEL_CLEARED_DURATION = 1.5
LEVEL_START_TITLE_DURATION = 2.5

# LEVEL EVENTS
LEVEL_NEXT_WAVE = event.custom_type()
LEVEL_CLEARED = event.custom_type()
LEVEL_GAME_OVER = event.custom_type()

# LEVEL SETTINGS
LEVEL_MAX_POWER_UPS = {
    1: 0,
    2: 1,
    3: 3,
}

# BULLET
MAX_BULLET_LEVEL = 2

BULLET0_IMG_PATH = "./assets/img/bullet_0.png"
BULLET0_SPEED = 6
BULLET0_DAMAGE = 1

BULLET1_IMG_PATH = "./assets/img/bullet_1.png"
BULLET1_SPEED = 6
BULLET1_DAMAGE = 2

BULLET_LEVEL_3_SPREAD = 12

# COLLECTIBLE
COLLECTIBLE_SPEED = 1
COLLECTIBLE_BASE_SCORE = 20
COLLECTIBLE_PROBABILITY = 0.35

EXTRA_SCORE_10_IMG_PATH = "./assets/img/collect_extra_score_10.png"

POWER_UP_IMG_PATH = "./assets/img/collect_power_up.png"
POWER_UP_PROBABILITY = 0.3
POWER_UP_SCORE = 10

# PLAYER
PLAYER_IMG_PATH = "./assets/img/player.png"
PLAYER_HEIGHT = 10
PLAYER_FIRE_DELAY = 0.3
PLAYER_LIVES = 3
PLAYER_HIT_DURATION = 0.5

# ENEMY
ENEMY_STATE_ENTRANCE = 0    # State when the enemy is entering the scene
ENEMY_STATE_ACTION = 1      # State when the enemy is acting normally (after entrance)

ENEMY_ENTRANCE_SPEED = 3
ENEMY_HIT_DURATION = 0.2

ENEMY_PARASITE_IMG_PATH = "./assets/img/enemy_parasite.png"
ENEMY_PARASITE_SPEED = 2
ENEMY_PARASITE_DOWN_SPEED = 0.1
ENEMY_PARASITE_BASE_FIRE_DELAY = 5
ENEMY_PARASITE_FIRE_DELAY_RANGE = 5
ENEMY_PARASITE_LIVES = 2
ENEMY_PARASITE_SCORE_KILL = 10

ENEMY_FLOODER_IMG_PATH = "./assets/img/enemy_flooder.png"
ENEMY_FLOODER_SPEED = 3
ENEMY_FLOODER_LIVES = 4
ENEMY_FLOODER_SCORE_KILL = 20
ENEMY_FLOODER_DOWN_FIRE_START_TIME = 3
ENEMY_FLOODER_DOWN_FIRE_DELAY = .05
ENEMY_FLOODER_DOWN_FIRE_STOP_TIME = 3.5
ENEMY_FLOODER_DOWN_MOVE_TIME = 4.5
ENEMY_FLOODER_U_SPEED = 3
ENEMY_FLOODER_U_MOVE_TIME = 2
ENEMY_FLOODER_U_BORDER_OFFSET = 20

ENEMY_GEAR_IMG0_PATH = "./assets/img/enemy_gear_0.png"
ENEMY_GEAR_IMG1_PATH = "./assets/img/enemy_gear_1.png"
ENEMY_GEAR_SPEED = 1
ENEMY_GEAR_FIRE_DELAY = 5
ENEMY_GEAR_LIVES = 10
ENEMY_GEAR_SCORE_KILL = 40
ENEMY_GEAR_FRAME_DURATION = 0.2 # Time between each frame in seconds
ENEMY_GEAR_WAVE_AMP = 40        # Wave amplitude
ENEMY_GEAR_WAVE_FREQ = 3        # Wave frequency in rads
ENEMY_GEAR_NBR_BULLETS = 16     # Number of bullets fired at once

ENEMY_BEAST_IMG_PATH = "./assets/img/enemy_beast.png"
ENEMY_BEAST_FIRE_START_TIME = 2.5
ENEMY_BEAST_FIRE_STOP_TIME = 3.5
ENEMY_BEAST_FIRE_DELAY = 0.3
ENEMY_BEAST_BULLET_SEPARATION = 10 # Half of the distance between the bullets
ENEMY_BEAST_LIVES = 60
ENEMY_BEAST_SCORE_KILL = 100
ENEMY_BEAST_WAVE_AMP = 30
ENEMY_BEAST_WAVE_FREQ = 0.2

ENEMY_TYPE_PARASITE = 0
ENEMY_TYPE_FLOODER_DOWN = 1
ENEMY_TYPE_FLOODER_U = 2
ENEMY_TYPE_GEAR = 3
ENEMY_TYPE_BEAST = 4

# SOUND
BG_MUSIC_PATH = "./assets/audio/space_warrior_soundtrack.mp3"
BG_MUSIC_VOL = 0.5

SFX_VOL = 1

CLICK_SOUND_PATH = "./assets/audio/click.wav"

GAME_CLEARED_SOUND_PATH = "./assets/audio/game_cleared.wav"

BULLET0_SOUND_PATH = "./assets/audio/player_bullet_0.wav"
BULLET1_SOUND_PATH = "./assets/audio/player_bullet_1.wav"
BULLET2_SOUND_PATH = "./assets/audio/player_bullet_1.wav"

PLAYER_HIT_SOUND_PATH = "./assets/audio/player_hit.wav"
PLAYER_DEATH_SOUND_PATH = "./assets/audio/player_death.wav"

EXTRA_SCORE_SOUND_PATH = "./assets/audio/extra_score.wav"
POWER_UP_SOUND_PATH = "./assets/audio/power_up.wav"

PARASITE_BULLET_SOUND_PATH = "./assets/audio/enemy_parasite_bullet.wav"
FLOODER_BULLET_SOUND_PATH = "./assets/audio/enemy_flooder_bullet.wav"
GEAR_BULLET_SOUND_PATH = "./assets/audio/enemy_gear_bullet.wav"
BEAST_BULLET_SOUND_PATH = "./assets/audio/enemy_beast_bullet.wav"
ENEMY_DEATH_SOUND_PATH = "./assets/audio/enemy_death.wav"