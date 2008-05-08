from math import sin, cos, atan, atan2, pi, fabs
from random import random, randint

import stats
import utils
import config
from objects import Object
from ships import Ship
from gfxs import *

class Weapon:
    def __init__( self, stats ):
        self.stats = stats
        self.lastFireAt = 0

    def canFire( self, ship, game ):
        return self.lastFireAt + self.stats.freqOfFire < game.tick

    def fire( self, ship, game ):
        self.lastFireAt = game.tick
        return ([],[],[])

    def getPoss( self, ship, game ):
       # poss = []
        for pos in ship.stats.weaponPositions:
            yield (ship.xp + pos.dist*cos(pos.angle+ship.ori), ship.yp + pos.dist*sin(pos.angle+ship.ori) )
       # return poss
     #   return [ (ship.xp + pos.dist*cos(pos.angle+ship.ori), ship.yp + pos.dist*sin(pos.angle+ship.ori) ) for pos in ship.stats.weaponPositions ]

class WeaponTurret( Weapon ):
    def canFire( self, ship, turret, game ):
     #   print self.lastFireAt, self.stats.freqOfFire, game.tick
        return Weapon.canFire( self, ship, game ) \
           and ship.energy >= turret.install.stats.energyPerUse \
           and ship.ore >= turret.install.stats.orePerUse

    def fire( self, ship, turret, game ):
        (ao,ro,gfxs) = Weapon.fire( self, ship, game )
        ship.energy = ship.energy - turret.install.stats.energyPerUse
        ship.ore = ship.ore - turret.install.stats.orePerUse
        return ([],[],gfxs)

    def getPoss( self, ship, turret, game ):
        turretPos = ship.getTurretPos( turret )
      #  poss = []
        for pos in turret.install.stats.weaponPositions:
            yield (turretPos[0] + pos.dist*cos(pos.angle+turret.rr+ship.ori), turretPos[1] + pos.dist*sin(pos.angle+turret.rr+ship.ori) )
      #  return poss

class LaserWeapon( Weapon ):
    def fire( self, ship, game, target ):
        (ao,ro,gfxs) = Weapon.fire( self, ship, game )
        for o in self.getPoss( ship, game ):
          (ao0, ro0, gfxs0) = self.hits( o, ship.ori, game, ship, target, ship.weapon )
          (ao, ro, gfxs) = (ao+ao0, ro+ro0, gfxs+gfxs0)
        return (ao,ro,gfxs)

    def hits( self, (xo,yo), ori, game, ship, target, weapon ):
        """Logic: compares the angle to target with the weapon orientation to atan( target.radius / dist between weapon and target )"""
        angle = utils.angleBetween( (xo,yo), (target.xp,target.yp) )
        dist = utils.distBetween( (xo,yo), (target.xp,target.yp) )
        angleSec = atan( float(target.stats.radius)/dist )
        diff = (ori-angle)%(2*pi)

        if diff < angleSec or 2*pi-diff < angleSec: ## hit!
            a = ori+pi
            hullBefore = target.hull
            (ao, ro, gfxs) = target.hit( game, pi+ori, ship.player, weapon.stats.energyDamage, weapon.stats.massDamage )  
            if hullBefore != target.hull: # went throught the shield
                d = ( target.xp+target.stats.maxRadius/4*cos(a), target.yp+target.stats.maxRadius/4*sin(a))
            else:
                d = ( target.xp+target.stats.maxRadius*cos(a), target.yp+target.stats.maxRadius*sin(a))
        else:
            (ao, ro, gfxs) = ([],[],[])
            d = ( xo + cos(ori)*weapon.stats.maxRange, yo + sin(ori)*weapon.stats.maxRange )
        
      #  print (xo,yo), max( ship.zp, target.zp)+1, d, weapon.stats.laserWidth, 0
        gfxs.append( GfxLaser( (xo,yo), max( ship.zp, target.zp)+1, d, weapon.stats.laserWidth, color=ship.player.race.type ) )
        
        return (ao, ro, gfxs) # (None, None)

class LaserWeaponTurret( WeaponTurret, LaserWeapon ):
    def fire( self, ship, turret, game, target ):
        (ao,ro,gfxs) = WeaponTurret.fire( self, ship, turret, game )
        for o in self.getPoss( ship, turret, game ):
          (ao0, ro0, gfxs0) = self.hits( o, ship.ori+turret.rr, game, ship, target, turret.weapon )
          (ao, ro, gfxs) = (ao+ao0, ro+ro0, gfxs+gfxs0)
        return (ao,ro,gfxs)

class MissileWeapon( Weapon ):
    def fire( self, ship, game, target ):
        (ao,ro,gfxs) = Weapon.fire( self, ship, game )
        for o in self.getPoss( ship, game ):
          ao.append( Missile( o, ship.zp, ship.ori, (ship.xi,ship.yi), target, ship, ship.weapon ) )
          gfxs.append( GfxExplosion( o, 10, sound=ids.S_EX_FIRE ) )
        return (ao,ro,gfxs)

class MissileWeaponTurret( WeaponTurret ):
    def fire( self, ship, turret, game, target ):
        (ao,ro,gfxs) = WeaponTurret.fire( self, ship, turret, game )
        for o in self.getPoss( ship, turret, game ):
         if ship.missiles[ turret.weapon.stats.projectile.img ].amount:
          ship.missiles[ turret.weapon.stats.projectile.img ].amount = ship.missiles[ turret.weapon.stats.projectile.img].amount-1
          if turret.install.stats.special == ids.S_NUKE:
              ao.append( NukeMissile( o, ship.zp, ship.ori+turret.rr, (ship.xi,ship.yi), ship.missiles[ turret.weapon.stats.projectile.img].target, ship, turret.weapon, turret.install.stats.specialValue ) )
          elif turret.install.stats.special == ids.S_PULSE:
              ao.append( PulseMissile( o, ship.zp, ship.ori+turret.rr, (ship.xi,ship.yi), ship.missiles[ turret.weapon.stats.projectile.img].target, ship, turret.weapon, turret.install.stats.specialValue ) )
          elif turret.install.stats.special == ids.S_MINER:
              ao.append( MinerMissile( o, ship.zp, ship.ori+turret.rr, (ship.xi,ship.yi), ship.missiles[ turret.weapon.stats.projectile.img].target, ship, turret.weapon, turret.install.stats.specialValue[0], turret.install.stats.specialValue[1], turret.install.stats.specialValue[2] ) )
          elif turret.install.stats.special == ids.S_COUNTER:
              ao.append( CounterMissile( o, ship.zp, ship.ori+turret.rr, (ship.xi,ship.yi), ship.missiles[ turret.weapon.stats.projectile.img].target, ship, turret.weapon, turret.install.stats.specialValue ) )
          else:
              ao.append( Missile( o, ship.zp, ship.ori+turret.rr, (ship.xi,ship.yi), target, ship, turret.weapon ) )
        #  ao.append( Missile( o, ship.zp, ship.ori+turret.rr, (ship.xi,ship.yi), target, ship, turret.weapon ) )
          gfxs.append( GfxExplosion( o, 10, sound=ids.S_EX_FIRE ) )
        return (ao,ro,gfxs)

    def canFire(self, ship, turret, game ):
        return WeaponTurret.canFire( self, ship, turret, game ) \
          and ship.missiles[ turret.weapon.stats.projectile.img].amount > 0 #  \
         # and ship.missiles[ turret.weapon.stats.projectile.img].target

class MassWeapon( Weapon ):
    def fire( self, ship, game, target ):
        (ao,ro,gfxs) = Weapon.fire( self, ship, game )
        angle = ship.ori
        speed = ship.weapon.stats.speed
        for o in self.getPoss( ship, game ):
     #   o = self.getPos( ship, game )
          i = ( ship.xi + speed*cos(angle), ship.yi + speed*sin(angle) )
          ao.append( Bullet( o, ship.zp, angle, i, target, ship, ship.weapon ) )
          gfxs.append( GfxExplosion( o, 3, sound=ids.S_EX_FIRE ) )
        return (ao,ro,gfxs)

class MassWeaponTurret( WeaponTurret ):
    def fire( self, ship, turret, game, target ):
        (ao,ro,gfxs) = WeaponTurret.fire( self, ship, turret, game )
        angle = (ship.ori+turret.rr)%(2*pi)
        speed = turret.weapon.stats.speed
    #    o = self.getPos( ship, game )
        for o in self.getPoss( ship, turret, game ):
          i = ( ship.xi+speed*cos(angle), ship.yi+speed*sin(angle) )
     #     print angle, i
          ao.append( Bullet( o, ship.zp, angle, i, target, ship, turret.weapon ) )
     #   print "bullet!"
          gfxs.append( GfxExplosion( o, 3, sound=ids.S_EX_FIRE ) )
        return (ao,ro,gfxs)



class Missile( Ship ):
    def __init__( self, (xp,yp), zp, ori, (xi,yi), target, launcher, weapon ):
        Ship.__init__( self, weapon.stats.projectile, None, xp, yp, zp, ori, xi, yi, 0, 0 )
        self.target = target
        self.launcher = launcher
        self.weapon = weapon
        self.maxRi = 0.01
        self.ttl = weapon.stats.projectileTtl #30*5
        self.originalTtl = weapon.stats.projectileTtl
        self.lostTarget = False
        self.thinkFreq = randint( 3, config.fps/2)

        self.xi = launcher.xi
        self.yi = launcher.yi

    def doTurn( self, game ):
        (ao,ro,ag) = Ship.doTurn(self, game)

        if self.inNebula and self.ttl%(config.fps*2)==0:
            self.loseTarget( game )

        if self.lostTarget and (self.originalTtl-self.ttl)>config.fps:
            self.launcher = None

        # detect hit
        for obj in game.objects:
             if obj.alive and obj.player and (not self.launcher or obj.player != self.launcher.player) \
               and utils.distLowerThanObjects( self, obj, self.stats.maxRadius + obj.stats.maxRadius ):
                 if self.launcher:
                     sender = self.launcher.player
                 else:
                     sender = None
                 (ao0, ro0, ag0) = obj.hit( game, utils.angleBetweenObjects( obj, self ), sender, self.weapon.stats.energyDamage, self.weapon.stats.massDamage )
                 (ao1, ro1, ag1) = self.explode( game )
                 (ao, ro, ag) = (ao+ao0+ao1, ro+ro0+ro1, ag+ag0+ag1)
                 break

        if self.alive and not (self.originalTtl-self.ttl)%self.thinkFreq:
            if isinstance( self.target, Object ):
                target = ( self.target.xp, self.target.yp )
                if not self.target.alive:
                    self.target = target
            else:
                target = self.target

        # ori
            destAngle = utils.angleBetween( (self.xp,self.yp), target )
            angle = utils.angleDiff( destAngle, self.ori )

            absAngle = fabs( angle )
            if absAngle > self.stats.maxRg: # *(config.fps/10): #*5:
                if angle > 0:
                    self.rg = self.stats.maxRg
                else:
                    self.rg = -1*self.stats.maxRg
            else:
                self.rg = 0

 	    self.thrust = self.stats.maxThrust
        

            if utils.distLowerThan( (self.xp,self.yp), target, self.stats.maxRadius*2 ):
                 (ao1, ro1, ag1) = self.explode( game )
                 (ao, ro, ag) = (ao+ao1, ro+ro1, ag+ag1)
             #    self.alive = False
            #     ro.append( self )
             #    ag.append( GfxExplosion( (self.xp,self.yp), self.stats.maxRadius*3 ) )
                
        if self.alive:
            if self.ttl == 0:
                self.alive = False
                ro.append( self )
            else:
                self.ttl = self.ttl - 1

        return (ao,ro,ag)

    def explode( self, game ):
        self.alive = False
        ro = [ self ]
        ag = [ GfxExplosion( (self.xp,self.yp), self.stats.maxRadius*3, sound=ids.S_EX_FIRE ) ]
        return ([],ro,ag)

    def loseTarget( self, game ):
        dist = randint( 0, 500 )
        angle = 2*pi*random()
        self.lostTarget = True
   #     self.launcher = None
        self.target = (self.xp+dist*cos(angle), self.yp+dist*sin(angle))

class NukeMissile( Missile ):
    def __init__( self, (xp,yp), zp, ori, (xi,yi), target, launcher, weapon, explosionRange ):
        Missile.__init__( self, (xp,yp), zp, ori, (xi,yi), target, launcher, weapon )
        self.explosionRange = explosionRange
        self.thinkFreq = config.fps/10

    def explode( self, game ):
        (ao,ro,ag) = ([],[],[])
        for obj in game.objects:
            if obj.alive and obj.player and utils.distLowerThanObjects( self, obj, self.explosionRange + obj.stats.maxRadius ):
                 if self.launcher:
                     sender = self.launcher.player
                 else:
                     sender = None
                 (ao0, ro0, ag0) = obj.hit( game, utils.angleBetweenObjects( obj, self ), sender, self.weapon.stats.energyDamage, self.weapon.stats.massDamage )
                 (ao, ro, ag) = (ao+ao0, ro+ro0, ag+ag0)
        self.alive = False
        ro0 = [ self ]
        ag0 = [ GfxExplosion( (self.xp,self.yp), self.explosionRange, sound=ids.S_EX_NUKE ) ]
        return (ao, ro+ro0, ag+ag0)

class PulseMissile( NukeMissile ):

    def explode( self, game ):
        (ao,ro,ag) = ([],[],[])
        for obj in game.objects:
            if obj.alive and obj.player and utils.distLowerThanObjects( self, obj, self.explosionRange + obj.stats.maxRadius ):
                 if self.launcher:
                     sender = self.launcher.player
                 else:
                     sender = None
                 (ao0, ro0, ag0) = obj.hit( game, utils.angleBetweenObjects( obj, self ), sender, self.weapon.stats.energyDamage, self.weapon.stats.massDamage, pulse=10*30 ) # self.weapon.stats.pulseLength
                 (ao, ro, ag) = (ao+ao0, ro+ro0, ag+ag0)
        self.alive = False
        ro0 = [ self ]
        ag0 = [ GfxExplosion( (self.xp,self.yp), self.explosionRange, sound=ids.S_EX_PULSE ) ]
        return (ao, ro+ro0, ag+ag0)

class MinerMissile( NukeMissile ):
    def __init__( self, (xp,yp), zp, ori, (xi,yi), target, launcher, weapon, explosionRange, nbrMines, minesRange ):
        NukeMissile.__init__( self, (xp,yp), zp, ori, (xi,yi), target, launcher, weapon, explosionRange )
        self.nbrMines = nbrMines
        self.minesRange = minesRange

    def explode( self, game ):
        (ao,ro,ag) = ([],[],[])

        for i in range( self.nbrMines ):
            dist = random()*self.explosionRange
            angle = random()*2*pi
            ao.append( Mine( (self.xp+cos(angle)*dist,self.yp+sin(angle)*dist), self.zp, (0,0), self.weapon, self.minesRange, self.minesRange/2 ) )

        self.alive = False
        ro0 = [ self ]
        ag0 = [ GfxExplosion( (self.xp,self.yp), self.explosionRange, sound=ids.S_EX_FIRE ) ]
        return (ao, ro+ro0, ag+ag0)

class CounterMissile( Missile ):
    def __init__( self, (xp,yp), zp, ori, (xi,yi), target, launcher, weapon, effectRange ):
        Missile.__init__( self, (xp,yp), zp, ori, (xi,yi), target, launcher, weapon )
        self.effectRange = effectRange
        self.t = 0

    def doTurn( self, game ):
        (ao,ro,ag) = Missile.doTurn(self, game)
        if self.t%(config.fps)/2 == 0: # fin missiles
            for obj in game.objects:
                if obj != self and isinstance( obj, Missile ) and utils.distLowerThanObjects( self, obj, self.effectRange ):
                     obj.target = self
        self.t += 1
        return (ao,ro,ag)

 #   def explode( self, game ):

class Bullet( Object ):
    def __init__( self, (xp,yp), zp, ori, (xi,yi), target, launcher, weapon ):
        Object.__init__( self, weapon.stats.projectile, xp, yp, zp, ori, xi, yi, 0, 0 )
        self.target = target
        self.launcher = launcher
        self.weapon = weapon
        self.ttl = 30 #*3

    def doTurn( self, game ):
        (ao,ro,ag) = Object.doTurn(self, game)

        # detect hit
        for obj in game.objects:
             if obj.alive and obj.player != None and obj.player != self.launcher.player \
               and utils.distLowerThanObjects( self, obj, self.stats.maxRadius + obj.stats.maxRadius ): # TODO better
                 (ao0, ro0, ag0) = obj.hit( game, utils.angleBetweenObjects( obj, self), self.launcher.player, energy=self.weapon.stats.energyDamage, mass=self.weapon.stats.massDamage )
               #  print self.weapon.stats.img, self.weapon.stats.energyDamage, self.weapon.stats.massDamage
                 (ao, ro, ag) = (ao+ao0, ro+ro0, ag+ag0)
                 self.alive = False
                 ro.append( self )
     #            ag.append( GfxExplosion( (self.xp,self.yp), self.stats.maxRadius ) )
                 break

        if self.alive and self.ttl == 0:
            self.alive = False
            ro.append( self )
        else:
            self.ttl = self.ttl - 1

        return (ao,ro,ag)

class Mine( Object ):
    def __init__( self, (xp,yp), zp, (xi,yi), weapon, explosionRange, detectionRange ):
        Object.__init__( self, stats.MINE, xp, yp, zp, random()*2*pi, xi, yi, 0, 0 ) # random()*0.01 )
        self.weapon = weapon
        self.ttl = 30*360 #weapon.stats.projectileTtl
        self.detectionRange = detectionRange
        self.explosionRange = explosionRange

    def doTurn( self, game ):
        (ao,ro,ag) = Object.doTurn(self, game)

        ## detect hit
        if not game.tick%20:
            for obj in game.objects:
                if obj.alive and obj.player and not isinstance( obj, Mine ) and utils.distLowerThanObjects( self, obj, self.detectionRange+obj.stats.maxRadius ):
                    (ao0,ro0,ag0) = self.explode( game )
                    (ao,ro,ag) = (ao+ao0,ro+ro0,ag+ag0)
                    break

        ## detect expiration
        if self.alive and self.ttl == 0:
            (ao0,ro0,ag0) = self.explode( game )
            (ao,ro,ag) = (ao+ao0,ro+ro0,ag+ag0)
        else:
            self.ttl = self.ttl - 1

        return (ao,ro,ag)

    def explode( self, game ):
        self.alive = False

        ao = []
        ro = [ self ]
        ag = [ GfxExplosion( (self.xp,self.yp), self.stats.maxRadius*3, sound=ids.S_EX_FIRE ) ]

        for obj in game.objects:
            if obj.alive and obj.player and utils.distLowerThanObjects( self, obj, self.explosionRange + obj.stats.maxRadius ):
                 (ao0, ro0, ag0) = obj.hit( game, utils.angleBetweenObjects( obj, self ), None, self.weapon.stats.energyDamage, self.weapon.stats.massDamage )
                 (ao, ro, ag) = (ao+ao0, ro+ro0, ag+ag0)

        return (ao,ro,ag)

