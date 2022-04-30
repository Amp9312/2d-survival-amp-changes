import random
from constants import *
from utils import *


BULLETS_FIRED = 0


class GameObjectContainer:
    def __init__(self, app):
        self.app = app
        self.gameList = []
        self.GRID = [[[] for _ in range(self.app.SCREEN_HEIGHT)] for _ in range(self.app.SCREEN_WIDTH)]
        self.n = 0

    def append(self, elem):
        x, y = self.gridCoord(elem)
        elem.gridCoord = (x, y)
        self.GRID[x][y].append(elem)
        self.gameList.append(elem)

    def getNearbyElements(self, elem):  # todo: rename to more general ie. getCollisionCandidates
        x, y = self.gridCoord(elem)
        lenx, leny = len(self.GRID), len(self.GRID[x])
        # currently checks up and down adjacent. not diagonal todo: maybe add that... maybe
        return self.GRID[x][y] + self.GRID[x-1][y] + self.GRID[x+1%lenx][y] + self.GRID[x][y-1] + self.GRID[x][y+1%leny]

    def gridCoord(self, elem):
        return int(elem.x/self.app.SCREEN_WIDTH), int(elem.y/self.app.SCREEN_HEIGHT)

    def updateObject(self, elem):
        x, y = self.gridCoord(elem)
        if elem not in self.GRID[x][y]:
            self.GRID[x][y].append(elem)
            oldx, oldy = elem.gridCoord
            self.GRID[oldx][oldy].remove(elem)
            elem.gridCoord = (x, y)

    def pop(self, i=None):
        x, y = self.gameList[i].gridCoord
        self.GRID[x][y].remove(self.gameList[i])
        return self.gameList.pop(i)

    def __len__(self):
        return len(self.gameList)

    def __getitem__(self, item):
        return self.gameList[item]

    def __iter__(self):
        self.n = 0
        return iter(self.gameList)

    def __next__(self):
        result = self.gameList[self.n]
        return result

    def clear(self):
        self.gameList.clear()


class BaseGameObject:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.is_alive = True
        self.moved = False
        self.gridCoord = (0, 0)

    def collide(self, other):
        raise NotImplementedError

    def bounceBack(self, other, bounceFactor=0.5):
        self.x += (self.x - other.x) * bounceFactor
        self.y += (self.y - other.y) * bounceFactor

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.U, self.V, self.w, self.h, 14)


class Creature(BaseGameObject):
    def __init__(self, x=0, y=0):
        super().__init__(x, y)
    pass


class Item(BaseGameObject):
    pass


# these can both probably inheret from something
class Scene:
    pass


class StateMachine:
    pass


class Point(BaseGameObject):
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.w, self.h = (10, 10)

    def collide(self, other):
        pass

    def update(self):
        pass

    def draw(self):
        pass


class Background:
    U = 32
    V = 32

    def __init__(self, width, height):
        self.tiles = []  # [[(int, int)]]
        self.width = width * WORLD_MULTIPLIER
        self.height = height * WORLD_MULTIPLIER

        opts = (1, -1)

        for _ in range(width * WORLD_MULTIPLIER):
            tmp = []
            for _ in range(height * WORLD_MULTIPLIER):
                tmp.append((random.choice(opts), random.choice(opts)))
            self.tiles.append(tmp)

    def update(self):
        pass

    def draw(self):
        for x in range(self.width):
            for y in range(self.height):
                #pyxel.pset(x, y, int(pyxel.noise(x, y))%16)
                pyxel.blt(x*BASE_BLOCK, y*BASE_BLOCK, 0, self.U, self.V, BASE_BLOCK * self.tiles[x][y][0], BASE_BLOCK * self.tiles[x][y][1])

        pass


class Ammo(BaseGameObject):
    U = 16
    V = 32
    w = 8
    h = 8

    def __init__(self, x, y, *args, **wkargs):
        super().__init__(x, y)
        self.ammoAmmount = 10

    def collide(self, other):
        if isinstance(other, Player):
            self.is_alive = False
            other.ammo += self.ammoAmmount

    def update(self):
        pass


class Brick(BaseGameObject):
    U = 24
    V = 40
    w = 8
    h = 8

    def __init__(self, x, y, gameObjects, app, placed = False):
        super().__init__(x, y)
        self.app = app
        self.gameObjects = gameObjects
        self.placed = placed
        self.amount = 10
        self.health = 100

    def collide(self, other):
        pass

    def takeDamage(self, amount):
        if self.placed:
            self.health -= amount
            pyxel.play(0, 8)

    def update(self):
        if self.health <= 0:
            self.die()

    def draw(self):
        if self.placed:
            super().draw()
        else:
            if pyxel.frame_count % 3 != 0:
                super().draw()

    def die(self, sound=True, score=0):
        self.is_alive = False
        self.app.gameObjects.append(Blast(self.x + ENEMY_WIDTH / 2, self.y + ENEMY_HEIGHT / 2))
        if sound:
            pyxel.play(1, 2)  # todo: distance from player affect volume level
        self.app.score += score


class Food(BaseGameObject):
    U = 16
    V = 40
    w = 8
    h = 8

    def __init__(self, x, y, *args, **kwargs):
        super().__init__(x, y)
        self.amount = 50

    def collide(self, other):
        self.is_alive = False

    def update(self):
        pass


class Health(BaseGameObject):
    U = 24
    V = 32
    w = 8
    h = 8

    def __init__(self, x, y, healthAmount=10):
        super().__init__(x, y)
        self.healthAmount = healthAmount

    def collide(self, other):
        if isinstance(other, Player):
            self.is_alive = False
            other.heal(self.healthAmount)

    def update(self):
        pass


class Player(Creature):
    U = 32
    V = 16
    MOVE_LEFT_KEY = pyxel.KEY_A
    MOVE_RIGHT_KEY = pyxel.KEY_D
    MOVE_UP_KEY = pyxel.KEY_W
    MOVE_DOWN_KEY = pyxel.KEY_S
    # MOVE_LEFT_KEY = pyxel.KEY_LEFT
    # MOVE_RIGHT_KEY = pyxel.KEY_RIGHT
    # MOVE_UP_KEY = pyxel.KEY_UP
    # MOVE_DOWN_KEY = pyxel.KEY_DOWN

    def __init__(self, x, y, gameObjects, app):
        super().__init__(x, y)
        self.app = app
        self.x = x
        self.y = y
        self.w = PLAYER_WIDTH
        self.h = PLAYER_HEIGHT
        self.is_alive = True
        self.gameObjects = gameObjects
        self.maxHealth = 100
        self.ammo = 10
        self.bricks = 0
        self.health = self.maxHealth
        self.hunger, self.maxHunger = (100, 100)
        self.damageCount = 0
        self.hungerCount = 0

    def moveControls(self):
        if pyxel.btn(self.MOVE_LEFT_KEY):
            self.x -= PLAYER_SPEED
        if pyxel.btn(self.MOVE_RIGHT_KEY):
            self.x += PLAYER_SPEED
        if pyxel.btn(self.MOVE_UP_KEY):
            self.y -= PLAYER_SPEED
        if pyxel.btn(self.MOVE_DOWN_KEY):
            self.y += PLAYER_SPEED
        self.app.gameObjects.updateObject(self)

    def shootControls(self):
        # shoot
        if self.ammo > 0:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.gameObjects.append(Bullet(
                    self.x + (PLAYER_WIDTH - BULLET_WIDTH) / 2, self.y - BULLET_HEIGHT / 2, point=Point(self.app.cursor.x, self.app.cursor.y)
                ))
                pyxel.play(0, 1)
                self.ammo -= 1
        if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            if self.bricks > 0:
                self.gameObjects.append(Brick(self.app.cursor.x, self.app.cursor.y, self.gameObjects, self.app, placed=True))
                self.bricks -= 1
        pass

    def update(self):
        if self.hunger <= 0:
            HUNGER_MULTIPLIER = 0.1
            self.health += self.hungerCount*HUNGER_MULTIPLIER
        if self.health <= 0:
            self.die(sound=True)
        self.moved = False
        # check for player boundary collision
        self.x = max(self.x, 0)
        self.x = min(self.x, WORLD_MULTIPLIER * pyxel.width - self.w)
        self.y = max(self.y, 0)
        self.y = min(self.y, WORLD_MULTIPLIER * pyxel.height - self.h)

        # move player
        if self.app.scene == SCENE_PLAY:
            self.moveControls()
            self.shootControls()

        self.hungerCount += 1

        if self.hungerCount > 3600 and self.hungerCount % 240 == 0: # after 2 minutes of not eating lose 1 point of hunger every 8 seconds
            self.hunger -= 1

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.U, self.V, self.w, self.h, 14)

    def die(self, sound=True, score=0):
        self.is_alive = False
        self.app.gameObjects.append(Blast(self.x + ENEMY_WIDTH / 2, self.y + ENEMY_HEIGHT / 2))
        if sound:
            pyxel.play(1, 2)  # todo: distance from player affect volume level
        self.app.score += score

    def takeDamage(self, amount):
        self.health -= amount
        pyxel.play(0, 6)
        if self.health <= 0:
            self.is_alive = False
            pyxel.play(0, 0)
            self.app.gameObjects.append(Blast(self.x + PLAYER_WIDTH / 2, self.y + PLAYER_HEIGHT / 2, ))
            self.app.scene = SCENE_GAMEOVER
            self.health = 100

    def heal(self, amount):
        self.health = self.health + amount if self.health + amount <= self.maxHealth else self.maxHealth
        pyxel.play(0, 7)

    def eat(self, amount):
        self.hunger += amount
        self.hungerCount = 0
        if self.hunger > self.maxHunger:
            self.hunger = self.maxHunger

    def collide(self, other):
        if isinstance(other, Enemy):
            self.takeDamage(other.damage)
            self.bounceBack(other)

        if isinstance(other, Brick):
            if not other.placed:
                self.bricks += other.amount
                other.is_alive = False
            else:
                self.bounceBack(other)
        if isinstance(other, Food):
            self.eat(other.amount)


class Bullet(BaseGameObject):
    w = BULLET_WIDTH
    h = BULLET_HEIGHT

    def __init__(self, x, y, dir=None, point=None, *args, **kwargs):
        super().__init__(x, y)
        global BULLETS_FIRED # generalize this to count all instances
        BULLETS_FIRED += 1
        if not dir and not point:
            raise Exception("both dir and point undefined. todo: fix this")
        if dir and point:
            raise Exception("both dir and point are defined. cmon, now")

        self.dirDict = {UP: (0, -1), DOWN: (0, 1), LEFT: (-1, 0), RIGHT: (1, 0)}
        self.x = x
        self.y = y
        self.w = BULLET_WIDTH
        self.h = BULLET_HEIGHT
        self.is_alive = True
        self.dir = dir
        self.point = point
        self.maxDistance = 40
        self.distance = 0
        self.current_speed = BULLET_SPEED
        self.minSpeed = 5
        self.damage = 25

    def update(self):
        self.moved = True
        if self.dir:
            self.x, self.y = self.x + self.current_speed*self.dirDict[self.dir][0], self.y + self.current_speed *self.dirDict[self.dir][1]
        if self.point:
            self.x, self.y, _, _ = stepToward(self.point, self, self.current_speed)
            if collision(self, self.point):
                self.is_alive = False
        self.distance += 1
        if self.distance > self.maxDistance:
            self.is_alive = False
        if self.current_speed > self.minSpeed:
            self.current_speed -= 1

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, BULLET_COLOR)

    def collide(self, other):
        self.is_alive = False


class Enemy(Creature):
    # U = 0
    # V = 16
    w = ENEMY_WIDTH
    h = ENEMY_HEIGHT

    def __init__(self, x, y, player, app):
        super().__init__(x, y)
        self.U, self.V = (random.choice([(32, 16), (48, 16), (48, 32), (48, 48)]))
        self.x = x
        self.y = y
        self.w = ENEMY_WIDTH
        self.h = ENEMY_HEIGHT
        self.dir = [1, 1]
        self.timer_offset = pyxel.rndi(0, 59)
        self.is_alive = True
        self.player = player
        self.app = app
        self.stepCount = 0
        self.state = self.stateInit
        self.dirtime = 0
        self.damage = 5
        self.targetPoint = BaseGameObject(random.randint(0, BASE_BLOCK*BLOCK_WIDTH), random.randint(0, BASE_BLOCK+BLOCK_HEIGHT))
        self.attackDistance = BASE_BLOCK * 10
        self.hunger, self.maxHunger = (100, 100)
        self.hungerCount = 0
        self.health = 100
        self.hungerStateLevel = 3

    def die(self, sound=True, score=0):
        self.is_alive = False
        self.app.gameObjects.append(Blast(self.x + ENEMY_WIDTH / 2, self.y + ENEMY_HEIGHT / 2))
        if sound:
            pyxel.play(1, 2)  # todo: distance from player affect volume level
        self.app.score += score

    def eat(self, amount):
        self.hunger += amount
        self.hungerCount = 0
        self.targetPoint = None
        if self.hunger > self.maxHunger:
            self.hunger = self.maxHunger

    def takeDamage(self, amount, sound=True):
        if sound:
            pyxel.play(0, 6)
        self.health -= amount
        if self.health <= 0:
            self.die(score=10)

    def collide(self, other):
        if isinstance(other, Bullet):
            self.takeDamage(other.damage)
        if isinstance(other, Player):
            self.bounceBack(other)
        if isinstance(other, Enemy):
            self.bounceBack(other)
        if isinstance(other, Brick):
            if other.placed:
                other.takeDamage(1)
                self.bounceBack(other)
        if isinstance(other, Food):
            self.eat(other.amount)
            self.targetPoint = None

    def debounceDir(self, w, h):
        if self.dir[0] != w or self.dir[1] != h and self.dirtime > 10:
            self.dir[0] = w
            self.dir[1] = h
            self.dirtime = 0
        self.dirtime += 1

        pass

    def stateInit(self):
        self.moved = False
        if self.stepCount > 30:
            self.stepCount = 0
            return random.choice([self.stateAttack, self.stateRandomWalk])
        return self.stateInit

    def stateLookForFood(self):
        if self.hunger > self.hungerStateLevel:
            if self.hunger >= self.maxHunger:
                return self.stateInit
            else:
                return random.choice([self.stateRandomWalk, self.stateLookForFood])
        nearbyFood = sorted([x for x in self.app.gameObjects.getNearbyElements(self) if isinstance(x, Food)], key=lambda x: distance(self, x))
        if nearbyFood:
            self.stepTowardPoint(nearbyFood[0])
        else:
            self.stateRandomWalk()
        return self.stateLookForFood

    # use this method in other places when stepping toward random point
    def stepTowardPoint(self, pnt=None):
        if not pnt or not self.targetPoint:
            randx, randy = random.randint(0, self.app.WORLD_WIDTH), random.randint(0, self.app.WORLD_HEIGHT)
            self.targetPoint = Point(randx, randy)
        else:
            self.targetPoint = pnt
        self.x, self.y, _, _ = stepToward(self.targetPoint, self, ENEMY_SPEED)

    def stateRandomWalk(self):
        self.moved = True
        if not self.targetPoint:
            randx, randy = random.randint(0, self.app.WORLD_WIDTH), random.randint(0, self.app.WORLD_HEIGHT)
            self.targetPoint = Point(randx, randy)
        if self.stepCount % 120 == 0:
            self.stepCount = 0
            self.targetPoint = None
            return random.choice([self.stateRandomWalk, self.stateInit, self.stateLookForFood])

        self.x, self.y, _, _ = stepToward(self.targetPoint, self, ENEMY_SPEED)
        self.app.gameObjects.updateObject(self)
        if self.player in self.app.gameObjects.getNearbyElements(self):
            if distance(self, self.player) < self.attackDistance and self.player.is_alive:
                self.stepCount = 0
                return self.stateAttack
        return self.stateRandomWalk

    def stateAttack(self):
        self.moved = True
        self.hunger -= 0.1
        if not self.player.is_alive:
            return self.stateRandomWalk
        self.x, self.y, h, w = stepToward(self.player, self, ENEMY_SPEED*3)
        self.app.gameObjects.updateObject(self)
        if self.stepCount > 240:
            self.stepCount = 0
            return random.choice([self.stateAttack, self.stateInit, self.stateRandomWalk])

        if distance(self, self.player) > self.attackDistance:
            self.stepCount = 0
            return self.stateRandomWalk

        return self.stateAttack

    def update(self):
        if self.hunger <= 0:
            if self.stepCount % 30 == 0:
                self.takeDamage(1, sound=False)
        self.moved = False
        if self.hunger < self.hungerStateLevel:
            self.state = self.stateLookForFood()
        else:
            self.state = self.state()
        self.stepCount += 1
        self.hungerCount += 1
        if self.hungerCount > 100 and self.hungerCount % 30 == 0:
            self.hunger -= 1

        pass

    def draw(self):
        pyxel.blt(self.x, self.y, 0, self.U, self.V, self.w * self.dir[0], self.h, 14)


class Cursor(BaseGameObject):
    def __init__(self, x, y, app):
        super().__init__()
        self.x = x
        self.y = y
        self.U = 48
        self.V = 0
        self.W = 16
        self.H = 16
        self.app = app

    def update(self):
        self.x = pyxel.mouse_x + (self.app.player.x - self.app.SCREEN_WIDTH/2)
        self.y = pyxel.mouse_y + (self.app.player.y - self.app.SCREEN_HEIGHT/2)

    def draw(self):
        pyxel.blt(self.x-8, self.y-8, 0, self.U, self.V, self.W, self.H, 14)

    def collide(self, other):
        pass


class Blast:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = BLAST_START_RADIUS
        self.is_alive = True

    def update(self):
        self.radius += 1
        if self.radius > BLAST_END_RADIUS:
            self.is_alive = False

    def draw(self):
        pyxel.circ(self.x, self.y, self.radius, BLAST_COLOR_IN)
        pyxel.circb(self.x, self.y, self.radius, BLAST_COLOR_OUT)

