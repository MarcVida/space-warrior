from __future__ import annotations
import pygame as pg
from settings import *
from audio import Audio
from random import random
from math import cos, sin, pi

# Base class for bullets
class Bullet(pg.sprite.Sprite):
    images: dict[str, pg.Surface] = {}
    def __init__(self, img_path: str, start_pos: tuple, direction: pg.Vector2 | int, speed: float, damage: int) -> None:
        super().__init__()
        if not img_path in Bullet.images.keys():
            Bullet.images[img_path] = pg.image.load(img_path).convert_alpha()
        self.image = Bullet.images[img_path]
        self.rect = self.image.get_rect(center = start_pos)
        self.damage = damage
        self.pos = start_pos

        # Set direction (if int: -1 = down, 1 = up) (if Vector2: normalize and assign)
        if isinstance(direction, int):
            assert direction != 0, "Bullet direction cannot be zero"
            self.direction = pg.Vector2(0, -direction).normalize()
        else:
            self.direction = direction.normalize()
        self.speed = speed

    def update(self) -> None:
        self.pos += self.direction * self.speed
        self.rect.center = self.pos
        if self.rect.left > GAME_WIDTH or self.rect.right < 0 or self.rect.top > WIN_HEIGHT or self.rect.bottom < 0:
            self.kill()

# Bullet 0
class Bullet0(Bullet):
    def __init__(self, start_pos: tuple, direction: pg.Vector2 | int) -> None:
        super().__init__(BULLET0_IMG_PATH, start_pos, direction, BULLET0_SPEED, BULLET0_DAMAGE)

# Bullet 1
class Bullet1(Bullet):
    def __init__(self, start_pos: tuple, direction: pg.Vector2 | int) -> None:
        super().__init__(BULLET1_IMG_PATH, start_pos, direction, BULLET1_SPEED, BULLET1_DAMAGE)

# Base class for collectibles
class Collectible(pg.sprite.Sprite):
    images: dict[str, pg.Surface] = {}
    def __init__(self, img_path: str, start_pos: tuple, score_extra: int = COLLECTIBLE_BASE_SCORE) -> None:
        super().__init__()
        if not img_path in Collectible.images.keys():
            Collectible.images[img_path] = pg.image.load(img_path).convert_alpha()
        self.image = Collectible.images[img_path]
        self.image = pg.transform.scale_by(self.image, 0.7)
        self.rect = self.image.get_rect(center = start_pos)
        self.score_extra = score_extra

    def apply(self, player: Player):
        player.score += self.score_extra

    def update(self) -> None:
        self.rect.centery += COLLECTIBLE_SPEED
        if self.rect.left > GAME_WIDTH or self.rect.right < 0 or self.rect.top > WIN_HEIGHT or self.rect.bottom < 0:
            self.kill()

# Collectible - Extra score 10
class ExtraScore10(Collectible):
    def __init__(self, start_pos: tuple) -> None:
        super().__init__(EXTRA_SCORE_10_IMG_PATH, start_pos)

    def apply(self, player: Player):
        super().apply(player)
        Audio.instance().play_extra_score_sound()

# Collectible - Power up
class PowerUp(Collectible):
    def __init__(self, start_pos: tuple) -> None:
        super().__init__(POWER_UP_IMG_PATH, start_pos, POWER_UP_SCORE)

    def apply(self, player: Player):
        super().apply(player)
        if player.bullet_level == MAX_BULLET_LEVEL:
            player.lives += 1
        else:
            player.bullet_level += 1
        Audio.instance().play_power_up_sound()

# Main player
class Player(pg.sprite.Sprite):
    _player = None  # Player singleton instance. Do not access it directly, instead use instance().
    def __init__(self) -> None:
        super().__init__()
        self.image = pg.image.load(PLAYER_IMG_PATH).convert_alpha()
        self.rect = self.image.get_rect(midbottom = (GAME_WIDTH//2, WIN_HEIGHT - PLAYER_HEIGHT))
        self.fire_timer = pg.time.get_ticks()
        self.bullet_level = 0 # Tracks the type of bullet you can fire
        self.lives = PLAYER_LIVES
        self.hit_timer = pg.time.get_ticks() - PLAYER_HIT_DURATION*1000
        self.score = 0
        Player._player = self

    @staticmethod
    def instance() -> Player:
        if not Player._player:
            raise RuntimeError("Tried to get uninitialized instance of Player")
        return Player._player

    def update(self) -> Bullet:
        # Set x coordinate
        self.rect.centerx = pg.mouse.get_pos()[0]
        if self.rect.right > GAME_WIDTH:
            self.rect.right = GAME_WIDTH
        elif self.rect.left < 0:
            self.rect.left = 0

        # Make transparent if hit
        if (pg.time.get_ticks() - self.hit_timer) < (PLAYER_HIT_DURATION*1000):
            self.image.set_alpha(125)
        else:
            self.image.set_alpha(255)

        # Create bullet & play bullet sound
        new_bullet = None
        left_click = pg.mouse.get_pressed()[0]
        can_fire = (pg.time.get_ticks() - self.fire_timer) >= (PLAYER_FIRE_DELAY * 1000)
        if left_click and can_fire:
            if self.bullet_level == 0:
                new_bullet = Bullet0((self.rect.centerx, self.rect.top), 1)
            elif self.bullet_level == 1:
                new_bullet = Bullet1((self.rect.centerx, self.rect.top), 1)
            elif self.bullet_level == 2:
                new_bullet = []
                new_bullet.append(Bullet0((self.rect.centerx - BULLET_LEVEL_3_SPREAD, self.rect.top), 1))
                new_bullet.append(Bullet1((self.rect.centerx, self.rect.top), 1))
                new_bullet.append(Bullet0((self.rect.centerx + BULLET_LEVEL_3_SPREAD, self.rect.top), 1))
            Audio.instance().play_player_bullet_sound(self.bullet_level)
            self.fire_timer = pg.time.get_ticks()

        return new_bullet
    
    def prepare_for_level(self):
        # Place the player in the middle (both rect and mouse)
        self.rect.midbottom = (GAME_WIDTH//2, WIN_HEIGHT - PLAYER_HEIGHT)
        pg.mouse.set_pos((GAME_WIDTH//2, WIN_HEIGHT//2))
        # Reset the fire timer (so that the player doesn't fire instantaneously)
        self.fire_timer = pg.time.get_ticks()
    
    def hit(self) -> None:
        if (pg.time.get_ticks() - self.hit_timer) < (PLAYER_HIT_DURATION*1000):
            return
        self.lives -= 1
        if self.bullet_level > 0:
            self.bullet_level -= 1
        self.hit_timer = pg.time.get_ticks()
        if self.lives <= 0:
            self.destroy()
        else:
            Audio.instance().play_player_hit_sound()

    def destroy(self) -> None:
        pg.event.post(pg.event.Event(LEVEL_GAME_OVER))

    def reset(self) -> None:
        self.lives = PLAYER_LIVES
        self.bullet_level = 0
        self.score = 0

# Base class for enemies
class Enemy(pg.sprite.Sprite):
    images: dict[str, pg.Surface] = {}
    def __init__(self, img_path: str, final_top_pos: tuple, fire_delay: float, lives: int, score_kill: int) -> None:
        super().__init__()
        if not img_path in Enemy.images.keys():
            Enemy.images[img_path] = pg.image.load(img_path).convert_alpha()
        self.image = pg.transform.scale_by(Enemy.images[img_path], 1) # Essentially clones the image
        self.rect = self.image.get_rect(midbottom = (final_top_pos[0], 0))
        self.final_top_pos = final_top_pos
        self.state = ENEMY_STATE_ENTRANCE
        self.base_fire_delay = fire_delay * 1000
        self.fire_timer = pg.time.get_ticks()
        self.lives = lives
        self.hit_timer = pg.time.get_ticks() - PLAYER_HIT_DURATION*1000
        self.score_kill = score_kill
        self.entrance_end_time = 0

    def update(self) -> Bullet:
        # Move from the top of the screen to its final position
        if self.state == ENEMY_STATE_ENTRANCE:
            self.rect.top += ENEMY_ENTRANCE_SPEED
            if self.rect.top >= self.final_top_pos[1]:
                self.rect.top = self.final_top_pos[1]
                self.entrance_end_time = pg.time.get_ticks()
                self.state = ENEMY_STATE_ACTION
        # Otherwise, kill enemy if out of bounds
        elif self.rect.left > GAME_WIDTH or self.rect.right < 0 or self.rect.top > WIN_HEIGHT or self.rect.bottom < 0:
            self.kill()
        
        # Make transparent if hit
        if (pg.time.get_ticks() - self.hit_timer) < (ENEMY_HIT_DURATION*1000):
            self.image.set_alpha(125)
        else:
            self.image.set_alpha(255)
        return None

    def hit(self, damage) -> tuple[int, Collectible]:
        self.lives -= damage
        self.hit_timer = pg.time.get_ticks()
        if self.lives <= 0:
            # Return a tuple containing the score for the kill and the collectible if applicable
            collectible = None
            if random() < COLLECTIBLE_PROBABILITY:
                if random() < POWER_UP_PROBABILITY:
                    collectible = PowerUp(self.rect.center)
                else:
                    collectible = ExtraScore10(self.rect.center)
            Audio.instance().play_enemy_death_sound()
            self.kill()
            return self.score_kill, collectible
        else:
            return 0, None

# Enemy - Parasite
class Parasite(Enemy):
    def __init__(self, final_top_pos: tuple, direction: int = 1) -> None:
        super().__init__(
            ENEMY_PARASITE_IMG_PATH, 
            final_top_pos, 
            ENEMY_PARASITE_BASE_FIRE_DELAY, 
            ENEMY_PARASITE_LIVES,
            ENEMY_PARASITE_SCORE_KILL)
        self.curr_fire_delay = self.base_fire_delay + random()*ENEMY_PARASITE_FIRE_DELAY_RANGE*1000
        self.direction = direction
        self.top = final_top_pos[1]

    def update(self) -> Bullet:
        super().update()
        # Move left/right
        if self.state == ENEMY_STATE_ACTION:
            self.top += ENEMY_PARASITE_DOWN_SPEED
            self.rect.top = int(self.top)
            if self.direction > 0:
                self.rect.right += ENEMY_PARASITE_SPEED
                if self.rect.right > GAME_WIDTH:
                    self.rect.right = GAME_WIDTH
                    self.direction *= -1
            else:
                self.rect.left -= ENEMY_PARASITE_SPEED
                if self.rect.left < 0:
                    self.rect.left = 0
                    self.direction *= -1

        new_bullet = None
        can_fire = (pg.time.get_ticks() - self.fire_timer) >= self.curr_fire_delay
        if can_fire:
            new_bullet = Bullet0((self.rect.centerx, self.rect.bottom), -1)
            self.fire_timer = pg.time.get_ticks()
            self.curr_fire_delay = self.base_fire_delay + random()*ENEMY_PARASITE_FIRE_DELAY_RANGE*1000
            Audio.instance().play_enemy_bullet_sound(ENEMY_TYPE_PARASITE)
        return new_bullet

# Enemy - Flooder Down (goes down only)
class FlooderDown(Enemy):
    def __init__(self, final_top_pos: tuple) -> None:
        super().__init__(ENEMY_FLOODER_IMG_PATH, 
                         final_top_pos, 
                         ENEMY_FLOODER_DOWN_FIRE_DELAY, 
                         ENEMY_FLOODER_LIVES, 
                         ENEMY_FLOODER_SCORE_KILL)
        self.fire_start_timer = pg.time.get_ticks()
        self.fire_stop_timer = pg.time.get_ticks()
        self.move_down_timer = pg.time.get_ticks()
    
    def update(self) -> None:
        super().update()
        new_bullet = None
        must_start = (pg.time.get_ticks() - self.fire_start_timer) >= ENEMY_FLOODER_DOWN_FIRE_START_TIME*1000
        must_stop = (pg.time.get_ticks() - self.fire_stop_timer) >= ENEMY_FLOODER_DOWN_FIRE_STOP_TIME*1000
        must_go_down = (pg.time.get_ticks() - self.move_down_timer) >= ENEMY_FLOODER_DOWN_MOVE_TIME*1000
        can_fire = (pg.time.get_ticks() - self.fire_timer) >= self.base_fire_delay

        if must_go_down:
            self.rect.centery += ENEMY_FLOODER_SPEED
        elif must_start and not must_stop:
            if can_fire:
                new_bullet = Bullet0((self.rect.centerx, self.rect.bottom), -1)
                Audio.instance().play_enemy_bullet_sound(ENEMY_TYPE_FLOODER_DOWN)
                self.fire_timer = pg.time.get_ticks()
        return new_bullet

# Enemy - Flooder U (displacement in a U-like shape)
class FlooderU(Enemy):
    def __init__(self, start_left: bool) -> None:
        super().__init__(ENEMY_FLOODER_IMG_PATH, 
                         (ENEMY_FLOODER_U_BORDER_OFFSET,ENEMY_FLOODER_U_BORDER_OFFSET) 
                            if start_left else 
                            (GAME_WIDTH-ENEMY_FLOODER_U_BORDER_OFFSET,ENEMY_FLOODER_U_BORDER_OFFSET), 
                         ENEMY_FLOODER_DOWN_FIRE_DELAY, 
                         ENEMY_FLOODER_LIVES, 
                         ENEMY_FLOODER_SCORE_KILL)
        self.direction = 1 if start_left else -1
        self.move_down_timer = pg.time.get_ticks()

    def update(self) -> None:
        super().update()
        must_go_down = (pg.time.get_ticks() - self.move_down_timer) >= ENEMY_FLOODER_U_MOVE_TIME*1000
        if must_go_down:
            self.rect.centerx += self.direction * ENEMY_FLOODER_U_SPEED
            self.rect.top = int(WIN_HEIGHT - ENEMY_FLOODER_U_BORDER_OFFSET - (WIN_HEIGHT - 2*ENEMY_FLOODER_U_BORDER_OFFSET)*(((2*(self.rect.centerx-ENEMY_FLOODER_U_BORDER_OFFSET)/(GAME_WIDTH-2*ENEMY_FLOODER_U_BORDER_OFFSET)) - 1)**2))
            if self.direction == 1 and self.rect.centerx > GAME_WIDTH - ENEMY_FLOODER_U_BORDER_OFFSET:
                self.rect.midtop = (GAME_WIDTH - ENEMY_FLOODER_U_BORDER_OFFSET, ENEMY_FLOODER_U_BORDER_OFFSET)
                self.direction = -1
                self.move_down_timer = pg.time.get_ticks()
            elif self.direction == -1 and self.rect.centerx < ENEMY_FLOODER_U_BORDER_OFFSET:
                self.rect.midtop = (ENEMY_FLOODER_U_BORDER_OFFSET, ENEMY_FLOODER_U_BORDER_OFFSET)
                self.direction = 1
                self.move_down_timer = pg.time.get_ticks()

# Enemy - Gear
class Gear(Enemy):
    def __init__(self, final_top_pos: tuple, direction: int = 1) -> None:
        super().__init__(ENEMY_GEAR_IMG0_PATH, 
                         final_top_pos, 
                         ENEMY_GEAR_FIRE_DELAY, 
                         ENEMY_GEAR_LIVES, 
                         ENEMY_GEAR_SCORE_KILL)
        self.images = [self.image, pg.image.load(ENEMY_GEAR_IMG1_PATH).convert_alpha()]
        self.curr_image_idx = 0
        self.animation_timer = pg.time.get_ticks()
        self.direction = direction

    def update(self) -> Bullet:
        super().update()
        # Move left/right and wave
        if self.state == ENEMY_STATE_ACTION:
            t = (pg.time.get_ticks() - self.entrance_end_time) / 1000
            self.rect.top = int(self.final_top_pos[1] + ENEMY_GEAR_WAVE_AMP*sin(ENEMY_GEAR_WAVE_FREQ*t))
            if self.direction > 0:
                self.rect.right += ENEMY_GEAR_SPEED
                if self.rect.right > GAME_WIDTH:
                    self.rect.right = GAME_WIDTH
                    self.direction *= -1
            else:
                self.rect.left -= ENEMY_GEAR_SPEED
                if self.rect.left < 0:
                    self.rect.left = 0
                    self.direction *= -1
        
        # Animation
        switch_image = (pg.time.get_ticks() - self.animation_timer) >= ENEMY_GEAR_FRAME_DURATION*1000
        if switch_image:
            self.curr_image_idx += 1
            self.curr_image_idx %= 2
            self.image = self.images[self.curr_image_idx]
            self.animation_timer = pg.time.get_ticks()

        # Fire bullets
        new_bullet = None
        can_fire = (pg.time.get_ticks() - self.fire_timer) >= self.base_fire_delay
        if can_fire:
            # Fire bullets in all directions
            new_bullet = []
            for i in range(ENEMY_GEAR_NBR_BULLETS):
                x = cos((i/ENEMY_GEAR_NBR_BULLETS)*2*pi)
                y = sin((i/ENEMY_GEAR_NBR_BULLETS)*2*pi)
                new_bullet.append(Bullet1(self.rect.center, pg.Vector2(x,y)))
            Audio.instance().play_enemy_bullet_sound(ENEMY_TYPE_GEAR)
            self.fire_timer = pg.time.get_ticks()
        return new_bullet

# Enemy - Beast
class Beast(Enemy):
    def __init__(self, final_top_pos: tuple) -> None:
        super().__init__(ENEMY_BEAST_IMG_PATH, 
                         final_top_pos, 
                         ENEMY_BEAST_FIRE_DELAY, 
                         ENEMY_BEAST_LIVES, 
                         ENEMY_BEAST_SCORE_KILL)
        self.image = pg.transform.scale_by(self.image, 2)
        self.rect = self.image.get_rect(midbottom = (final_top_pos[0], 0))
        self.fire_start_timer = pg.time.get_ticks()
        self.fire_stop_timer = pg.time.get_ticks()
        
    def update(self) -> Bullet:
        super().update()
        # Move in circles
        if self.state == ENEMY_STATE_ACTION:
            t = (pg.time.get_ticks() - self.entrance_end_time) / 1000
            self.rect.centerx = self.final_top_pos[0] + int(ENEMY_BEAST_WAVE_AMP * sin(ENEMY_BEAST_WAVE_FREQ*t*2*pi))
            self.rect.top = self.final_top_pos[1] + ENEMY_BEAST_WAVE_AMP  - int(ENEMY_BEAST_WAVE_AMP * cos(ENEMY_BEAST_WAVE_FREQ*t*2*pi))

        # Firing sequence
        new_bullet = None
        can_do_fire_sequence = (pg.time.get_ticks() - self.fire_start_timer) >= ENEMY_BEAST_FIRE_START_TIME*1000
        if can_do_fire_sequence:
            can_fire = (pg.time.get_ticks() - self.fire_timer) >= self.base_fire_delay
            if can_fire:
                player_pos_vect = pg.Vector2(Player.instance().rect.center)
                bullet0_pos = (self.rect.midbottom[0] - ENEMY_BEAST_BULLET_SEPARATION, self.rect.midbottom[1])
                bullet1_pos = (self.rect.midbottom[0] + ENEMY_BEAST_BULLET_SEPARATION, self.rect.midbottom[1])
                new_bullet = []
                new_bullet.append(Bullet1(bullet0_pos, player_pos_vect - pg.Vector2(bullet0_pos)))
                new_bullet.append(Bullet1(bullet1_pos, player_pos_vect - pg.Vector2(bullet1_pos)))
                Audio.instance().play_enemy_bullet_sound(ENEMY_TYPE_BEAST)
                self.fire_timer = pg.time.get_ticks()
            should_stop_firing = (pg.time.get_ticks() - self.fire_stop_timer) >= ENEMY_BEAST_FIRE_STOP_TIME*1000
            if should_stop_firing:
                self.fire_start_timer = pg.time.get_ticks()
                self.fire_stop_timer = pg.time.get_ticks()
        return new_bullet