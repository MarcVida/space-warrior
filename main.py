import pygame as pg
from settings import *
from sprites import *
from levels import Level
from audio import Audio

# GAME SETUP
pg.init()
screen = pg.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
pg.display.set_icon(pg.image.load(WIN_ICON_PATH))
pg.display.set_caption(GAME_TITLE)
pg.mouse.set_visible(DEBUG)
clock = pg.time.Clock()
title_font = pg.font.Font(TITLE_FONT_PATH, TITLE_FONT_SIZE)
subtitle_font = pg.font.Font(SUBTITLE_FONT_PATH, SUBTITLE_FONT_SIZE)
audio = Audio.instance()

curr_level_idx = 0
game_state = STATE_START
level_cleared_timer = 0
level_title_timer = 0
last_score = 0              # Score from the last game played

game_title_text = title_font.render(GAME_TITLE, None, TITLE_COLOR)
game_title_rect = game_title_text.get_rect(center = (GAME_WIDTH//2, (WIN_HEIGHT - TITLE_FONT_SIZE)//2))
game_subtitle_text = subtitle_font.render(GAME_SUBTITLE, None, SUBTITLE_COLOR)
game_subtitle_rect = game_subtitle_text.get_rect(center = (GAME_WIDTH//2, (WIN_HEIGHT + TITLE_FONT_SIZE)//2))
level_cleared_text = title_font.render(LEVEL_CLEARED_TEXT, None, "white")
level_cleared_rect = level_cleared_text.get_rect(center = (GAME_WIDTH//2, WIN_HEIGHT//2))

game_over_text = title_font.render(GAME_OVER_TEXT, None, TITLE_COLOR)
game_over_rect = game_over_text.get_rect(center = (GAME_WIDTH//2, WIN_HEIGHT//2 - TITLE_FONT_SIZE))
game_over_subtitle_text = subtitle_font.render(GAME_OVER_SUBTITLE, None, SUBTITLE_COLOR)
game_over_subtitle_rect = game_over_subtitle_text.get_rect(center = (GAME_WIDTH//2, WIN_HEIGHT//2))

game_cleared_text = title_font.render(GAME_CLEARED_TEXT, None, TITLE_COLOR)
game_cleared_rect = game_cleared_text.get_rect(center = (GAME_WIDTH//2, WIN_HEIGHT//2 - TITLE_FONT_SIZE))
game_cleared_subtitle_text = subtitle_font.render(GAME_CLEARED_SUBTITLE, None, SUBTITLE_COLOR)
game_cleared_subtitle_rect = game_cleared_subtitle_text.get_rect(center = (GAME_WIDTH//2, WIN_HEIGHT//2))

bg_front = pg.image.load(BG_FRONT_PATH).convert_alpha()
bg_front.set_alpha(100)
bg_front_rect = bg_front.get_rect()
bg_front_pos_x = float(bg_front_rect.left)
bg_back = pg.image.load(BG_BACK_PATH).convert_alpha()
bg_back.set_alpha(100)
bg_back_rect = bg_back.get_rect()
bg_back_pos_x = float(bg_back_rect.left)
bg_direction = -1

# GAME FUNCTIONS
def handle_events():
    global running, game_state
    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            running = False
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == STATE_START:
                start_first_level()
            elif game_state == STATE_GAME_CLEARED:
                audio.play_click_sound()
                game_state = STATE_START
            elif game_state == STATE_GAME_OVER:
                audio.play_click_sound()
                game_state = STATE_START
        elif event.type == LEVEL_NEXT_WAVE:
            get_curr_level().next_wave()
        elif event.type == LEVEL_CLEARED:
            handle_level_cleared()
        elif event.type == LEVEL_GAME_OVER:
            handle_game_over()

def draw_background():
    screen.fill("black")
    if game_state == STATE_PLAY:
        screen.blit(bg_back, bg_back_rect)
        screen.blit(bg_front, bg_front_rect)
    pg.draw.rect(screen, "black", pg.Rect(GAME_WIDTH+1, 0, WIN_WIDTH-GAME_WIDTH-1, WIN_HEIGHT))
    pg.draw.line(screen, "white", (GAME_WIDTH+1,0), (GAME_WIDTH+1,WIN_HEIGHT))

def update_background():
    global bg_front_pos_x, bg_back_pos_x, bg_direction
    bg_front_pos_x += bg_direction * BG_FRONT_SPEED
    bg_back_pos_x = bg_front_pos_x * BG_BACK_POS_RATIO
    bg_front_rect.left = int(bg_front_pos_x)
    bg_back_rect.left = int(bg_back_pos_x)
    if bg_direction > 0 and bg_front_rect.left > 0:
        bg_front_rect.left = 0
        bg_direction = -1
    elif bg_direction < 0 and bg_front_rect.right < WIN_WIDTH:
        bg_front_rect.right = WIN_WIDTH
        bg_direction = 1

def get_curr_level():
    return Level.all_levels[curr_level_idx]

def handle_level_cleared():
    global game_state, level_cleared_timer
    get_curr_level().clear()
    game_state = STATE_LEVEL_CLEARED
    level_cleared_timer = pg.time.get_ticks()

def handle_game_over():
    global game_state, last_score
    get_curr_level().clear()
    last_score = Player.instance().score
    Player.instance().reset()
    audio.stop_bg_music()
    audio.play_player_death_sound()
    game_state = STATE_GAME_OVER

def handle_game_cleared():
    global game_state, last_score
    last_score = Player.instance().score
    Player.instance().reset()
    audio.stop_bg_music()
    audio.play_game_cleared_sound()
    game_state = STATE_GAME_CLEARED

def draw_level_cleared():
    screen.blit(level_cleared_text, level_cleared_rect)

def start_first_level():
    global curr_level_idx, game_state, level_title_timer
    curr_level_idx = 0
    get_curr_level().start()
    audio.play_bg_music()
    audio.play_click_sound()
    level_title_timer = pg.time.get_ticks()
    game_state = STATE_PLAY

def start_next_level():
    global curr_level_idx, game_state, level_title_timer
    curr_level_idx += 1
    if curr_level_idx >= len(Level.all_levels):
        handle_game_cleared()
    else:
        get_curr_level().start()
        level_title_timer = pg.time.get_ticks()
        game_state = STATE_PLAY

def draw_game_title():
    screen.blit(game_title_text, game_title_rect)
    screen.blit(game_subtitle_text, game_subtitle_rect)

def draw_level_title():
    level_title_text = title_font.render(get_curr_level().title, None, TITLE_COLOR)
    level_title_rect = level_title_text.get_rect(center = (GAME_WIDTH//2, (WIN_HEIGHT - TITLE_FONT_SIZE)//2))
    level_subtitle_text = subtitle_font.render(get_curr_level().subtitle, None, SUBTITLE_COLOR)
    level_subtitle_rect = level_subtitle_text.get_rect(center = (GAME_WIDTH//2, (WIN_HEIGHT + TITLE_FONT_SIZE)//2))

    screen.blit(level_title_text, level_title_rect)
    screen.blit(level_subtitle_text, level_subtitle_rect)

def draw_game_over():
    score_text = subtitle_font.render(f"Your score: {last_score}", None, SUBTITLE_COLOR)
    score_rect = score_text.get_rect(center = (GAME_WIDTH//2, WIN_HEIGHT//2 + TITLE_FONT_SIZE))

    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)
    screen.blit(game_over_subtitle_text, game_over_subtitle_rect)

def draw_game_cleared():
    score_text = subtitle_font.render(f"Your score: {last_score}", None, SUBTITLE_COLOR)
    score_rect = score_text.get_rect(center = (GAME_WIDTH//2, WIN_HEIGHT//2 + TITLE_FONT_SIZE))

    screen.blit(game_cleared_text, game_cleared_rect)
    screen.blit(score_text, score_rect)
    screen.blit(game_cleared_subtitle_text, game_cleared_subtitle_rect)

def show_debug_info():
    pg.display.set_caption(f"FPS: {clock.get_fps(): .2f}")

# MAIN LOOP
running = True
while running:
    handle_events()
    draw_background()
    update_background()

    if game_state == STATE_START:
        draw_game_title()
    elif game_state == STATE_PLAY:
        get_curr_level().draw(screen)
        get_curr_level().update()
        if (pg.time.get_ticks() - level_title_timer) < (LEVEL_START_TITLE_DURATION*1000):
            draw_level_title()
    elif game_state == STATE_LEVEL_CLEARED:
        draw_level_cleared()
        if (pg.time.get_ticks() - level_cleared_timer) >= (LEVEL_CLEARED_DURATION*1000):
            start_next_level()
    elif game_state == STATE_GAME_CLEARED:
        draw_game_cleared()
    elif game_state == STATE_GAME_OVER:
        draw_game_over()

    if DEBUG: show_debug_info()
    pg.display.flip()
    clock.tick(FRAME_RATE)

# GAME EXIT
pg.quit()