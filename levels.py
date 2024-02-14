from __future__ import annotations
import pygame as pg
from settings import *
from sprites import *

class EnemyRecord:
    def __init__(self, enemy_type: int, main_arg: tuple, args) -> None:
        self.enemy_type = enemy_type
        self.main_arg = main_arg        # Mandatory argument (e.g. position)
        self.args = args                # Extra arguments

    def __repr__(self) -> str:
        return f"(enemy_type={self.enemy_type}, pos={self.main_arg})"
    
class LevelStats:
    def __init__(self) -> None:
        self.font = pg.font.Font(STATS_FONT_PATH, STATS_FONT_SIZE)
    
    def get_pos(self, index: int):
        assert index >=0 and index < STATS_LEN, f"Invalid stat index: {index}"
        return (GAME_WIDTH + STATS_LEFT, (STATS_CENTERY + int(STATS_HEIGHT*(-0.5 + index/(STATS_LEN-1)))))

    def draw(self, surface: pg.Surface, level_id: int, score: int, lives: int, pow_level: int) -> None:
        level_text = self.font.render(f"Level {level_id}", None, STATS_COLOR)
        level_rect = level_text.get_rect(midleft = self.get_pos(0))
        score_text = self.font.render(f"Score: {score}", None, STATS_COLOR)
        score_rect = score_text.get_rect(midleft = self.get_pos(1))
        lives_text = self.font.render(f"Lives: {lives}", None, STATS_COLOR)
        lives_rect = lives_text.get_rect(midleft = self.get_pos(2))
        pow_level_text = self.font.render(f"Power level: {pow_level}", None, STATS_COLOR)
        pow_level_rect = pow_level_text.get_rect(midleft = self.get_pos(3))

        surface.blit(level_text, level_rect)
        surface.blit(score_text, score_rect)
        surface.blit(lives_text, lives_rect)
        surface.blit(pow_level_text, pow_level_rect)

    def update(self):
        pass

class Level:
    all_levels: list[Level] = []
    player: pg.sprite.GroupSingle = None
    stats: LevelStats = None

    def __init__(self, level_nbr, title: str, subtitle: str) -> None:
        self.level_nbr = level_nbr
        self.title = title
        self.subtitle = subtitle
        self.enemy_schedule: dict[float,list[EnemyRecord]] = {}
        self.enemy_stack: list[tuple[float,list[EnemyRecord]]] = []
        self.enemies = pg.sprite.Group()
        self.player_bullets = pg.sprite.Group()
        self.enemy_bullets = pg.sprite.Group()
        self.collectibles = pg.sprite.Group()
        self.power_up_count = 0
        Level.all_levels.append(self)

    def add_enemy(self, time: float, enemy_type: int, main_arg, *args):
        if time not in self.enemy_schedule.keys():
            self.enemy_schedule[time] = []
        self.enemy_schedule[time].append(EnemyRecord(enemy_type, main_arg, args))

    def start(self):
        if not Level.player:
            Level.player = pg.sprite.GroupSingle(Player())
        if not Level.stats:
            Level.stats = LevelStats()
        self.power_up_count = 0
        self.player.sprite.prepare_for_level()
        self.enemies.empty()
        assert self.enemy_schedule, "Cannot start a level with an empty enemy schedule"
        self.enemy_stack = sorted(self.enemy_schedule.items(), key = lambda x: x[0])
        self.set_next_wave_timer(0)
        if DEBUG:
            print(f"FIRST WAVE: {self.enemy_stack[0]}")

    def next_wave(self):
        prev_time, new_enemies = self.enemy_stack.pop(0)
        for record in new_enemies:
            if record.enemy_type == ENEMY_TYPE_PARASITE:
                if record.args:
                    self.enemies.add(Parasite(record.main_arg, record.args[0]))
                else: self.enemies.add(Parasite(record.main_arg))
            elif record.enemy_type == ENEMY_TYPE_FLOODER_DOWN:
                self.enemies.add(FlooderDown(record.main_arg))
            elif record.enemy_type == ENEMY_TYPE_FLOODER_U:
                self.enemies.add(FlooderU(record.main_arg))
            elif record.enemy_type == ENEMY_TYPE_GEAR:
                if record.args:
                    self.enemies.add(Gear(record.main_arg, record.args[0]))
                else: self.enemies.add(Gear(record.main_arg))
            elif record.enemy_type == ENEMY_TYPE_BEAST:
                self.enemies.add(Beast(record.main_arg))
        if self.enemy_stack:
            self.set_next_wave_timer(prev_time)
        if DEBUG:
            next_wave_enemies = []
            if self.enemy_stack:
                next_wave_enemies = self.enemy_stack[0]
            print(f"NEXT WAVE: {next_wave_enemies}")

    def set_next_wave_timer(self, prev_time) -> None:
        pg.time.set_timer(LEVEL_NEXT_WAVE, 1000*(self.enemy_stack[0][0] - prev_time), 1)

    def clear(self):
        pg.time.set_timer(LEVEL_NEXT_WAVE, 0)
        self.enemy_stack.clear()
        self.enemies.empty()
        self.player_bullets.empty()
        self.enemy_bullets.empty()
        self.collectibles.empty()
        self.power_up_count = 0

    def add_collectible(self, collectible: Collectible):
        if collectible:
            if type(collectible) == PowerUp:
                if self.power_up_count == LEVEL_MAX_POWER_UPS[self.level_nbr]:
                    if DEBUG: print(f"Power up killed because maximum number is reached")
                    collectible.kill()
                    return
                else:
                    self.power_up_count += 1
            if DEBUG: print(f"Collectible added: {type(collectible)}")
            self.collectibles.add(collectible)

    def draw(self, surface: pg.Surface):
        self.stats.draw(surface, 
                        self.level_nbr, 
                        self.player.sprite.score, 
                        self.player.sprite.lives, 
                        self.player.sprite.bullet_level)
        self.player_bullets.draw(surface)
        self.enemy_bullets.draw(surface)
        self.collectibles.draw(surface)
        self.player.draw(surface)
        self.enemies.draw(surface)

    def update(self):
        # Update level stats
        self.stats.update()

        # Update player (and add player bullet)
        new_bullet = self.player.sprite.update()
        if new_bullet:
            if isinstance(new_bullet, list):
                for bullet in new_bullet:
                    self.player_bullets.add(bullet)
            else:
                self.player_bullets.add(new_bullet)
        
        # Check for collision with enemy bullet
        enemy_bullet_sprites = self.enemy_bullets.sprites()
        enemy_bullet_rects = [s.rect for s in enemy_bullet_sprites]
        collision_idx = self.player.sprite.rect.collidelist(enemy_bullet_rects)
        if collision_idx != -1:
            self.player.sprite.hit()
            enemy_bullet_sprites[collision_idx].kill()

        # Check for collision with collectible
        collectible_sprites = self.collectibles.sprites()
        collectible_rects = [s.rect for s in collectible_sprites]
        collision_idx = self.player.sprite.rect.collidelist(collectible_rects)
        if collision_idx != -1:
            collectible_sprites[collision_idx].apply(self.player.sprite)
            collectible_sprites[collision_idx].kill()

        # Update enemies (and add enemy bullets)
        curr_enemies = self.enemies.sprites()
        for enemy in curr_enemies:
            # Update enemy and add bullet
            new_bullet = enemy.update()
            if new_bullet:
                self.enemy_bullets.add(new_bullet)

            # Check for collision with player
            if enemy.rect.colliderect(self.player.sprite.rect):
                score_kill, collectible = enemy.hit(enemy.lives) # Simply kill the enemy
                self.player.sprite.score += score_kill
                self.player.sprite.hit()
                self.add_collectible(collectible)
                continue
            
            # Check for collision with player bullet
            player_bullet_sprites = self.player_bullets.sprites()
            player_bullet_rects = [s.rect for s in player_bullet_sprites]
            collision_idx = enemy.rect.collidelist(player_bullet_rects)
            if collision_idx != -1:
                # Increment score, add collectible and kill bullet
                score_kill, collectible = enemy.hit(player_bullet_sprites[collision_idx].damage)
                self.player.sprite.score += score_kill
                # If a collectible is generated, add it to its group unless the max limit of power ups is reached
                self.add_collectible(collectible)
                player_bullet_sprites[collision_idx].kill()

        # Update bullets
        self.player_bullets.update()
        self.enemy_bullets.update()
        self.collectibles.update()

        # Check if level is cleared
        if (not self.enemy_stack) and (not self.enemies.sprites()) and (not self.collectibles.sprites()):
            pg.event.post(pg.event.Event(LEVEL_CLEARED))

level1 = Level(1, "LEVEL 1", "Where it all begins")

level1.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2, 50))
level1.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 30, 50))
level1.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 30, 50))

level1.add_enemy(6, ENEMY_TYPE_PARASITE, (GAME_WIDTH - 30, 100), -1)
level1.add_enemy(6, ENEMY_TYPE_PARASITE, (GAME_WIDTH - 60, 100), -1)
level1.add_enemy(6, ENEMY_TYPE_PARASITE, (GAME_WIDTH - 90, 100), -1)
level1.add_enemy(6, ENEMY_TYPE_PARASITE, (30, 100))
level1.add_enemy(6, ENEMY_TYPE_PARASITE, (60, 100))
level1.add_enemy(6, ENEMY_TYPE_PARASITE, (90, 100))

level1.add_enemy(10, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 15, 50), -1)
level1.add_enemy(10, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 45, 50), -1)
level1.add_enemy(10, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 75, 50), -1)
level1.add_enemy(10, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 105, 50), -1)
level1.add_enemy(10, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 15, 50))
level1.add_enemy(10, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 45, 50))
level1.add_enemy(10, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 75, 50))
level1.add_enemy(10, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 105, 50))

level1.add_enemy(18, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 + 80, 50))
level1.add_enemy(18, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 - 80, 50))

level1.add_enemy(22, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 + 140, 80))
level1.add_enemy(22, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 - 140, 80))

level1.add_enemy(24, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 + 200, 100))
level1.add_enemy(24, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2, 100))
level1.add_enemy(24, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 - 200, 100))

level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 15, 50), -1)
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 45, 50), -1)
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 75, 50), -1)
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 105, 50), -1)
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 135, 50), -1)
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 15, 50))
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 45, 50))
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 75, 50))
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 105, 50))
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 135, 50))

level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 15, 100), -1)
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 45, 100), -1)
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 75, 100), -1)
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 105, 100), -1)
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 135, 100), -1)
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 15, 100))
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 45, 100))
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 75, 100))
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 105, 100))
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 135, 100))

level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 15, 150), -1)
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 45, 150), -1)
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 75, 150), -1)
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 105, 150), -1)
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 135, 150), -1)
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 15, 150))
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 45, 150))
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 75, 150))
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 105, 150))
level1.add_enemy(26, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 135, 150))

level1.add_enemy(30, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 15, 200), -1)
level1.add_enemy(30, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 45, 200), -1)
level1.add_enemy(30, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 75, 200), -1)
level1.add_enemy(30, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 105, 200), -1)
level1.add_enemy(30, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 15, 200))
level1.add_enemy(30, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 45, 200))
level1.add_enemy(30, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 75, 200))
level1.add_enemy(30, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 105, 200))

level1.add_enemy(35, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 + 40, 50))
level1.add_enemy(35, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 - 40, 50))

""" #level1.add_enemy(4, ENEMY_TYPE_FLOODER_U, True)
level1.add_enemy(4, ENEMY_TYPE_GEAR, (GAME_WIDTH//2 - 100, 100))
#level1.add_enemy(4, ENEMY_TYPE_BEAST, (GAME_WIDTH//2 - 100, 150))
#level1.add_enemy(5, ENEMY_TYPE_FLOODER_U, False)
level1.add_enemy(5, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 80, 50), -1)
level1.add_enemy(10, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 + 80, 90)) """

level2 = Level(2, "LEVEL 2", "Tensions are rising")

level2.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 30, 100), -1)
level2.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 60, 100), -1)
level2.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 90, 100), -1)
level2.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 30, 100))
level2.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 60, 100))
level2.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 90, 100))

level2.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 30, 150), -1)
level2.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 60, 150), -1)
level2.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 90, 150), -1)
level2.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 120, 150), -1)
level2.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 30, 150))
level2.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 60, 150))
level2.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 90, 150))
level2.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 120, 150))

level2.add_enemy(5, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 15, 200), -1)
level2.add_enemy(5, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 45, 200), -1)
level2.add_enemy(5, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 75, 200), -1)
level2.add_enemy(5, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 105, 200), -1)
level2.add_enemy(5, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 135, 200), -1)
level2.add_enemy(5, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 15, 200))
level2.add_enemy(5, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 45, 200))
level2.add_enemy(5, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 75, 200))
level2.add_enemy(5, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 105, 200))
level2.add_enemy(5, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 135, 200))

level2.add_enemy(10, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 - 80, 100))
level2.add_enemy(10, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 - 240, 50))
level2.add_enemy(10, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 + 80, 100))
level2.add_enemy(10, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 + 240, 50))

level2.add_enemy(15, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 + 160, 100))
level2.add_enemy(15, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2, 100))
level2.add_enemy(15, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 - 160, 100))

level2.add_enemy(17, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 30, 50), -1)
level2.add_enemy(17, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 60, 50), -1)
level2.add_enemy(17, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 90, 50), -1)
level2.add_enemy(17, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 120, 50), -1)
level2.add_enemy(17, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 30, 50))
level2.add_enemy(17, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 60, 50))
level2.add_enemy(17, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 90, 50))
level2.add_enemy(17, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 120, 50))

level2.add_enemy(20, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 30, 150), -1)
level2.add_enemy(20, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 60, 150), -1)
level2.add_enemy(20, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 90, 150), -1)
level2.add_enemy(20, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 120, 150), -1)
level2.add_enemy(20, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 30, 150))
level2.add_enemy(20, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 60, 150))
level2.add_enemy(20, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 90, 150))
level2.add_enemy(20, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 120, 150))

level2.add_enemy(20, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 15, 200), -1)
level2.add_enemy(20, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 45, 200), -1)
level2.add_enemy(20, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 75, 200), -1)
level2.add_enemy(20, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 105, 200), -1)
level2.add_enemy(20, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 135, 200), -1)
level2.add_enemy(20, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 15, 200))
level2.add_enemy(20, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 45, 200))
level2.add_enemy(20, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 75, 200))
level2.add_enemy(20, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 105, 200))
level2.add_enemy(20, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 135, 200))

level2.add_enemy(25, ENEMY_TYPE_FLOODER_U, False)

level2.add_enemy(33, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 30, 150), -1)
level2.add_enemy(33, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 60, 150), -1)
level2.add_enemy(33, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 90, 150), -1)
level2.add_enemy(33, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 120, 150), -1)
level2.add_enemy(33, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 30, 150))
level2.add_enemy(33, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 60, 150))
level2.add_enemy(33, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 90, 150))
level2.add_enemy(33, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 120, 150))

level2.add_enemy(35, ENEMY_TYPE_FLOODER_U, True)
level2.add_enemy(37, ENEMY_TYPE_FLOODER_U, False)

level2.add_enemy(40, ENEMY_TYPE_GEAR, (50, 100))

level2.add_enemy(44, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 30, 100), -1)
level2.add_enemy(44, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 60, 100), -1)
level2.add_enemy(44, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 90, 100), -1)
level2.add_enemy(44, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 30, 100))
level2.add_enemy(44, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 60, 100))
level2.add_enemy(44, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 90, 100))
level2.add_enemy(44, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 30, 150), -1)
level2.add_enemy(44, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 60, 150), -1)
level2.add_enemy(44, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 90, 150), -1)
level2.add_enemy(44, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 120, 150), -1)
level2.add_enemy(44, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 30, 150))
level2.add_enemy(44, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 60, 150))
level2.add_enemy(44, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 90, 150))
level2.add_enemy(44, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 120, 150))

level2.add_enemy(46, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 30, 50), -1)
level2.add_enemy(46, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 60, 50), -1)
level2.add_enemy(46, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 90, 50), -1)
level2.add_enemy(46, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 120, 50), -1)
level2.add_enemy(46, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 30, 50))
level2.add_enemy(46, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 60, 50))
level2.add_enemy(46, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 90, 50))
level2.add_enemy(46, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 120, 50))

level2.add_enemy(48, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 15, 200), -1)
level2.add_enemy(48, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 45, 200), -1)
level2.add_enemy(48, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 75, 200), -1)
level2.add_enemy(48, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 105, 200), -1)
level2.add_enemy(48, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 135, 200), -1)
level2.add_enemy(48, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 15, 200))
level2.add_enemy(48, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 45, 200))
level2.add_enemy(48, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 75, 200))
level2.add_enemy(48, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 105, 200))
level2.add_enemy(48, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 135, 200))

level2.add_enemy(49, ENEMY_TYPE_GEAR, (GAME_WIDTH - 50, 100), -1)

level3 = Level(3, "LEVEL 3", "The end is near")

level3.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 15, 50), -1)
level3.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 45, 50), -1)
level3.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 75, 50), -1)
level3.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 105, 50), -1)
level3.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 135, 50), -1)
level3.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 15, 50))
level3.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 45, 50))
level3.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 75, 50))
level3.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 105, 50))
level3.add_enemy(3, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 135, 50))

level3.add_enemy(4, ENEMY_TYPE_GEAR, (50, 100))
level3.add_enemy(5, ENEMY_TYPE_GEAR, (GAME_WIDTH - 50, 100), -1)

level3.add_enemy(6, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 30, 150), -1)
level3.add_enemy(6, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 60, 150), -1)
level3.add_enemy(6, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 90, 150), -1)
level3.add_enemy(6, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 120, 150), -1)
level3.add_enemy(6, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 30, 150))
level3.add_enemy(6, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 60, 150))
level3.add_enemy(6, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 90, 150))
level3.add_enemy(6, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 120, 150))

level3.add_enemy(8, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 - 80, 200))
level3.add_enemy(8, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 - 240, 200))
level3.add_enemy(8, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 + 80, 200))
level3.add_enemy(8, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 + 240, 200))

level3.add_enemy(9, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 15, 100), -1)
level3.add_enemy(9, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 45, 100), -1)
level3.add_enemy(9, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 75, 100), -1)
level3.add_enemy(9, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 105, 100), -1)
level3.add_enemy(9, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 135, 100), -1)
level3.add_enemy(9, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 15, 100))
level3.add_enemy(9, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 45, 100))
level3.add_enemy(9, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 75, 100))
level3.add_enemy(9, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 105, 100))
level3.add_enemy(9, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 135, 100))

level3.add_enemy(13, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 + 240, 100))
level3.add_enemy(13, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 + 120, 100))
level3.add_enemy(13, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2, 100))
level3.add_enemy(13, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 - 120, 100))
level3.add_enemy(13, ENEMY_TYPE_FLOODER_DOWN, (GAME_WIDTH//2 - 240, 100))

level3.add_enemy(22, ENEMY_TYPE_BEAST, (GAME_WIDTH//2, 80))

level3.add_enemy(25, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 15, 50), -1)
level3.add_enemy(25, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 45, 50), -1)
level3.add_enemy(25, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 75, 50), -1)
level3.add_enemy(25, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 105, 50), -1)
level3.add_enemy(25, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 135, 50), -1)
level3.add_enemy(25, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 15, 50))
level3.add_enemy(25, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 45, 50))
level3.add_enemy(25, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 75, 50))
level3.add_enemy(25, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 105, 50))
level3.add_enemy(25, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 135, 50))

level3.add_enemy(30, ENEMY_TYPE_FLOODER_U, False)

level3.add_enemy(40, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 15, 150), -1)
level3.add_enemy(40, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 45, 150), -1)
level3.add_enemy(40, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 75, 150), -1)
level3.add_enemy(40, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 105, 150), -1)
level3.add_enemy(40, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 135, 150), -1)
level3.add_enemy(40, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 15, 150))
level3.add_enemy(40, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 45, 150))
level3.add_enemy(40, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 75, 150))
level3.add_enemy(40, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 105, 150))
level3.add_enemy(40, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 135, 150))

level3.add_enemy(40, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 30, 100), -1)
level3.add_enemy(40, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 60, 100), -1)
level3.add_enemy(40, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 90, 100), -1)
level3.add_enemy(40, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 120, 100), -1)
level3.add_enemy(40, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 30, 100))
level3.add_enemy(40, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 60, 100))
level3.add_enemy(40, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 90, 100))
level3.add_enemy(40, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 120, 100))

level3.add_enemy(50, ENEMY_TYPE_BEAST, (100, 50))
level3.add_enemy(50, ENEMY_TYPE_BEAST, (GAME_WIDTH - 100, 50))

level3.add_enemy(55, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 15, 50), -1)
level3.add_enemy(55, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 45, 50), -1)
level3.add_enemy(55, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 75, 50), -1)
level3.add_enemy(55, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 105, 50), -1)
level3.add_enemy(55, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 - 135, 50), -1)
level3.add_enemy(55, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 15, 50))
level3.add_enemy(55, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 45, 50))
level3.add_enemy(55, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 75, 50))
level3.add_enemy(55, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 105, 50))
level3.add_enemy(55, ENEMY_TYPE_PARASITE, (GAME_WIDTH//2 + 135, 50))