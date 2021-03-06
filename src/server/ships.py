from objects import Object, Sun
from math import sqrt, pow, atan, pi, sin, cos, fabs, hypot

from common.comms import COObject
from common.utils import *
from common.gfxs import *
from common import config

class OreBatch:
    def __init__(self, amount, pos=0):
        self.amount = int(amount)
        self.pos = pos

class Ship( Object ):
    def __init__( self, stats, ai, xp, yp, zp=0, ori=0.0, xi=0, yi=0, zi=0, ri=0, thrust=0 ):
        Object.__init__( self, stats, xp, yp, zp, ori, xi, yi, zi, ri )

        self.alive = True
        self.maxOri = 2*pi

        self.thrust = thrust
        self.rg = 0

        self.shieldVsMass = self.stats.shieldVsMass
        self.shieldVsEnergy = self.stats.shieldVsEnergy
        self.hullVsMass = self.stats.hullVsMass 
        self.hullVsEnergy = self.stats.hullVsEnergy

        self.ai = ai
        self.dockedTo = False
        self.dockedAt = 0 # tick at docking

        self.hull = stats.maxHull
        self.shield = stats.maxShield
        self.inertiaControl = True

        self.headed = True # differentiate bases from ships

        self.pulsedUntil = -1000
        self.inNebula = False # variable state
        self.inertiaMod = 1
        self.thrustBoost = 0

        self.shipyards = [] # list of regulard shipyards
        self.guestDocked = [] # list of temporary docks

    def getRadiusAt( self, ang ): # absolute angle with another object
        return self.stats.maxRadius

    def doTurn(self, game):
        # ai
        if self.ai:
            ( addedObjects0, removedObjects0, addedGfxs0 ) = self.ai.doTurn( self, game )
        else:
            ( addedObjects0, removedObjects0, addedGfxs0 ) = ([],[],[])

        if not self.orbiting and self.pulsedUntil < game.tick:
            # engine thrust
            self.xi = self.xi + self.thrust * cos( self.ori )
            self.yi = self.yi + self.thrust * sin( self.ori )

            # gouvernailstats
            self.ri = self.ri + self.rg

            # inertia controls
            self.xi = self.xi * (0.9+0.01*self.stats.mass)*self.inertiaMod #0.9
            self.yi = self.yi * (0.9+0.01*self.stats.mass)*self.inertiaMod #0.9
            self.zi = self.zi * (0.9+0.01*self.stats.mass)*self.inertiaMod #0.9
            if fabs(self.xi) < 0.05 and fabs(self.yi) < 0.05:
                self.xi = self.yi = 0

            if self.inertiaControl:
                self.ri = self.ri * 0.9 # *self.inertiaMod
                if fabs(self.ri) < 0.0005:
                    self.ri = 0

        if (not self.ai or self.ai.dockingTo) and randint( 0, config.fps*10 ) == 0:
        #    zDiff = -2 + 4*randint( 0, 1 )
            nz = randint( -5, 5 )
            can = True
            for obj in game.objects.getWithinArea( self, self.stats.maxRadius+500 ):
            #    print "s ", obj.zp <= max( self.zp, nz ), obj.zp >= min( self.zp, nz ), areOver( self, obj )
                if obj != self and obj.zp <= max( self.zp, nz ) and obj.zp >= min( self.zp, nz ) and areOver( self, obj ):
                    can = False
                    break
         #   print "switch", can, nz, obj.zp <= max( self.zp, nz ), obj.zp >= min( self.zp, nz ), areOver( self, obj )
            if can:
                self.zp = nz
                    
 
        ( addedObjects1, removedObjects1, addedGfxs1 ) = Object.doTurn( self, game )
#        if self.thrust > 0 and self.stats.engines:
#            if randint( 0, 4 ) == 0:
#                engine = choice( self.stats.engines )
#                (x,y) = (self.xp+engine[0]*cos(self.ori+engine[1]), self.yp+engine[0]*sin(self.ori+engine[1]) )
#                addedGfxs1.append( GfxExhaust( (x,y), self.zp, 0, -0.2*self.xi+(0.5-random())*0.4, -0.2*self.yi+(0.5-random())*0.4, random()*pi ) )

        if game.tick%(config.fps)==11:
            self.inNebula = False
            for obj in game.astres:
                if isinstance( obj, Nebula ) and distLowerThanObjects( self, obj, self.stats.maxRadius+obj.stats.maxRadius):
                    self.inNebula = True
                    break

        return ( addedObjects0+addedObjects1, removedObjects0+removedObjects1, addedGfxs0+addedGfxs1 )

    def enterHangar( self ):
        self.xi = 0
        self.yi = 0
        self.zi = 0
        self.ri = 0

    def hit( self, game, angle, sender, energy=0, mass=0, pulse=False ):
      if self.alive:
        if sender and self.player:
            rel = game.getRelationBetween( self.player, sender )
            if pulse:
                relDamage = 100
            else:
                relDamage = energy+mass
            game.setRelationBetween( self.player, sender, max(-100,rel-relDamage) )

        if self.ai:
            self.ai.hitted( self, game, angle, sender, energy, mass, pulse )
        gfxs = []

        damageToShield = min( self.shield, energy*self.shieldVsEnergy + mass*self.shieldVsMass )

        if damageToShield > 0:
            gfxs.append( GfxShield( (self.xp, self.yp), self.stats.maxRadius, self.shield/self.stats.maxShield, angle, damageToShield ) )

        rEnergy = max( 0, energy-self.shield)
        rMass = max( 0, mass-max( 0, self.shield-energy)*5)
        self.shield = self.shield - damageToShield # max( 0, self.shield - energy - mass/3) 

        damageToHull = min( self.hull, rEnergy*self.hullVsEnergy + rMass*self.hullVsMass)
        self.hull = self.hull - damageToHull #- rMass - rEnergy/3

        if self.hull == 0: # dead
            if sender:
                print sender.points, self.stats.pointsWorth
                sender.points = sender.points + self.stats.pointsWorth
            (ao0, ro0, ag0 ) = self.die( game )
            return (ao0,ro0,ag0+gfxs)
        else: # alive
            if pulse:
                self.pulsedUntil = game.tick + pulse
        #        print game.tick + pulse, game.tick, pulse
                if self.shield >1:
                    gfxs.append( GfxShield( (self.xp, self.yp), self.stats.maxRadius, self.shield/self.stats.maxShield, 0, 1000 ) )
                self.shield = self.shield/2

            if damageToHull > 0:
                gfxs.append( GfxExplosion( (self.xp+cos(angle)*self.stats.maxRadius/2,self.yp+sin(angle)*self.stats.maxRadius/2), damageToHull, sound=ids.S_EX_FIRE ) ) # TODO place explosion at hit
            return ([],[],gfxs)
      return ([],[],[])

    def die( self, game ):
        self.alive = False
        if self.ai:
            self.ai.died( self, game )
        gfxs = [ GfxExplosion( (self.xp,self.yp), self.stats.maxRadius, sound=ids.S_EX_SHIP) ]
        if self.stats.unavoidableFragments:
           for f in self.stats.unavoidableFragments:
              gfxs.append( GfxFragment( (self.xp, self.yp), self.zp, self.ori, self.xi+(0.5-random())*0.4, self.yi+(0.5-random())*0.4, self.ri+(0.5-random())*0.02, f, randint( int(1.5*self.stats.maxRadius), 2*self.stats.maxRadius ) ) )

        if self.stats.fragments:
            for i in range( int(self.stats.maxRadius/10) ):#f in self.stats.fragments[1:]:
                f = choice( self.stats.fragments )
                gfxs.append( GfxFragment( (self.xp+randint(-1*self.stats.maxRadius,self.stats.maxRadius), self.yp+randint(-1*self.stats.maxRadius,self.stats.maxRadius)), self.zp, random()*2*pi, self.xi+(0.5-random())*0.4, self.yi+(0.5-random())*0.4, (0.5-random())*0.3, f, randint( int(1.5*self.stats.maxRadius), int(2.5*self.stats.maxRadius) ) ) )

        for i in range( 0, randint(1,3*self.stats.maxRadius) ):
            i = randint( 1, 3*self.stats.maxRadius )
            (xi,yi) = ( self.xi+(0.5-random())*0.4, self.yi+(0.5-random())*0.4 )
            gfxs.append( GfxExplosion( (self.xp+randint(-1*self.stats.maxRadius,self.stats.maxRadius)+xi*i, self.yp+randint(-1*self.stats.maxRadius,self.stats.maxRadius)+yi*i), self.stats.maxRadius/(2+random()*3), delai=i ) )
        return ([],[self],gfxs) 

from ais import * # useless?
from weapons import * # useless?
from turrets import *

class ShipWithTurrets( Ship ):
    def __init__( self, player, stats, ai, xp, yp, zp=0, ori=0.0, xi=0, yi=0, zi=0, ri=0, thrust=0 ):
        Ship.__init__( self, stats, ai, xp, yp, zp, ori, xi, yi, zi, ri, thrust )
        self.player = player
        self.turrets = []
        self.turretPoss = {} # [None]*len(stats.turrets)
        for turret in stats.turrets:
            self.turrets.append( Turret( turret, self ) ) # , None, AiWeaponTurret() ) )

        # install standard turrets
        for turret,turretStat in zip(self.turrets,stats.defaultTurrets):
            if turretStat:
                turret.buildInstall( turretStat )

    def getCommObjects(self):
        objects = []
        for turret in self.turrets:
          if not turret.stats.overShip:
            if isinstance( turret, BuildableTurret ) and turret.building:
                t = ids.T_BUILDING
            elif turret.install:
                t = turret.install.stats.type
            else:
                t = None
            if t:
                (x,y) = self.getTurretPos( turret )
                objects.append( COObject( t, x, y, self.zp, self.ori+turret.rr, None, 10 ) )

        objects.append( COObject( self.stats.img, self.xp, self.yp, self.zp, self.ori, None, self.stats.maxRadius  ) )

        for turret in self.turrets:
          if turret.stats.overShip:
            if isinstance( turret, BuildableTurret ) and turret.building:
                t = ids.T_BUILDING
            elif turret.install:
                t = turret.install.stats.type
            else:
                t = None
            if t:
                (x,y) = self.getTurretPos( turret )
                objects.append( COObject( t, x, y, self.zp, self.ori+turret.rr, None, 10 ) )

        return objects

    def doTurn(self,game):
        prevPos = (self.xp, self.yp, self.ori)
        res = Ship.doTurn( self, game )
        pastPos = (self.xp, self.yp, self.ori)
        if prevPos != pastPos:
            self.turretPoss = {} # [None]*len(stats.turrets)
        return res

    def getTurretPos(self,turret):
        try:
       # if self.turretPoss.has_key( turret ):
            return self.turretPoss[ turret ]
      #  else:
        except KeyError:
            r = self.ori + turret.stats.distAngle
            x = int(self.xp) + turret.stats.dist*cos( r )
            y = int(self.yp) + turret.stats.dist*sin( r )
            self.turretPoss[ turret ] = (x,y)
            return (x,y)

class ShipSingleWeapon( Ship ):
    def __init__( self, player, stats, ai, xp, yp, zp=0, ori=0.0, xi=0, yi=0, zi=0, ri=0, thrust=0 ):
        Ship.__init__( self, stats, ai, xp, yp, zp, ori, xi, yi, zi, ri, thrust )
        self.player = player
        if stats.weapon.weaponType == ids.WT_MASS or stats.weapon.weaponType == ids.WT_BOMB:
            self.weapon = MassWeapon( stats.weapon )
        elif stats.weapon.weaponType == ids.WT_LASER:
            self.weapon = LaserWeapon( stats.weapon )
        elif stats.weapon.weaponType == ids.WT_MISSILE:
            self.weapon = MissileWeapon( stats.weapon )
        else:
            raise Warning(  "warning: weapon not mass, laser nor missile: %s" % stats.weapon.weaponType )

        self.hull = self.stats.maxHull
# TODO add different weapon typee for bombs
  #      self.zp = 1

class Builder:
    def __init__( self ):
        self.building = None
        self.goal = 0
        self.buildAt = 0

class Shipyard:
    def __init__( self ):
        self.building = None
	self.buildCost = 0
	self.build = 0
	self.away = []
	self.docked = []

    def getCount( self ):
        return len(self.away)+len(self.docked)

class MissileReserve:
    def __init__( self ):
        self.building = None
	self.buildCost = 0
	self.build = 0
	self.amount = 0
	self.target = None

from weapons import explode
class JumperShip:
    def __init__( self ):
        self.jumping = None

        self.jumpCharge = 0
        self.jumpRecover = 0

        self.jumpChargeDelay = config.fps*3
        self.jumpRecoverDelay = config.fps*10

    def doTurn( self, game ):
        (ao,ro,ag) = ([],[],[]) 

        ## Jumps
        if self.jumping:
            self.jumpCharge += 1 
            if self.jumpCharge >= self.jumpChargeDelay:
                (ao0,ro0,ag0) = self.jump( self.jumping, game )
                (ao,ro,ag) = (ao+ao0,ro+ro0,ag+ag0) 
                self.ai.goTo( self, self.pos )
                self.jumping = False
                self.jumpRecover = self.jumpRecoverDelay #config.fps*10 # TODO set variable value in stats?
                self.jumpCharge = 0
        elif self.jumpRecover:
            self.jumpRecover -= 1

        return (ao,ro,ag)

    def canJump( self, game ):
        if not self.inNebula:
         #  and self.jumping:
            for obj in game.objects.getWithinArea( self, self.stats.maxRadius+1000 ):
                if isinstance( obj, FlagShip ):
                    for turret in obj.turrets:
                        if turret.install and turret.activated and turret.install.stats.special == ids.S_INTERDICTOR and distLowerThanObjects( self, obj, self.stats.maxRadius+turret.install.stats.specialValue):
                            return False
            return True
        else:
            return False


    def jump( self, (xd, yd), game  ):
        if self.canJump( game ):
          angleToDest = utils.angleBetween( self.pos, (xd,yd) )
          gfxs = [GfxJump((self.xp,self.yp),self.stats.maxRadius, angle=angleToDest )]

          self.xp, self.yp = xd, yd
          self.ai.goingTo = None
          gfxs.append( GfxJump((self.xp,self.yp),self.stats.maxRadius, angle=angleToDest+pi) )
          self.jumping = False
          self.turretPoss = {}
          return ([],[],gfxs)
        else:
          return ([],[],[])

    def delayedJump( self, (xd,yd), delay=None ):
        if self.jumping:
            charge = self.jumpCharge
        else:
            charge = 0

        if delay:
            self.jumpChargeDelay = int(delay)

        self.jumping = (xd, yd)
        self.jumpCharge = charge

        
class FlagShip( ShipWithTurrets, JumperShip ):
    def __init__( self, player, stats, ai, xp, yp, zp=0, ori=0.0, xi=0, yi=0, zi=0, ri=0, thrust=0 ):
        self.player = player
        

        # resources
        self.processLength = 60*30
        self.oreProcess = [] # list of OreBatch # (amount,position<chainLength)
        self.ore = stats.maxOre/2
        self.energy = stats.maxEnergy/2

        self.repairing = True
        self.charging = True
        self.lastRepairsAt = 0
        self.repairDelay = 10
        
        self.civilianShips = []
        self.civilianValue = 1

        self.lastLaunchAt = 0

        ShipWithTurrets.__init__( self, player, stats, ai, xp, yp, zp, ori, xi, yi, zi, ri, thrust )
        JumperShip.__init__( self )

        self.turrets = []
        for turret in stats.turrets:
            self.turrets.append( BuildableTurret( turret, self ) )

        for turret,turretStat in zip(self.turrets,stats.defaultTurrets):
            if turretStat:
                turret.buildInstall( turretStat )

        self.shipyards = {}
        if player:
            for s in player.race.ships:
                self.shipyards[ s.img ] = Shipyard()

        for shipStats, count in stats.defaultShips:
            for i in xrange( count ):
                self.shipyards[ shipStats.img ].docked.append( buildShip( self.player, shipStats, 0,0, flagship=self ) )

        self.missiles = {}
        if player:
            for m in player.race.missiles:
                self.missiles[ m ] = MissileReserve()


        self.noOreCloseAt = -1000

        
        self.selfDestructCommand = False
        
    def doTurn( self, game ):
        self.inertiaMod = 1
        
        solarSailEfficiency = 0
        darkExtractorEfficiency = 0
        darkEngineEfficiency = 0
        
        nebulaOreSum = 0
        
        oldOre = self.ore
        oldEnergy = self.energy
        
        self.shieldVsMass = self.stats.shieldVsMass
        self.shieldVsEnergy = self.stats.shieldVsEnergy
        self.hullVsMass = self.stats.hullVsMass 
        self.hullVsEnergy = self.stats.hullVsEnergy

       ## build
        # turrets
        for turret in self.turrets:
          if turret.building:
            turret.build += self.getBuildRate()
            if turret.build >= turret.buildCost:
                turret.buildInstall( turret.building )

          if turret.install and turret.activated:
              if turret.install.stats.orePerFrame <= self.ore \
                and turret.install.stats.energyPerFrame <= self.energy:
                  self.energy = self.energy-turret.install.stats.energyPerFrame
                  self.ore = self.ore-turret.install.stats.orePerFrame
              else:
                  turret.activated = False
              if turret.activated:
                  if turret.install.stats.special == ids.S_SUCKER and self.inNebula and game.tick%(config.fps/3)==6: # sucker creates ore when in nebula
                      nebulaOreSum += turret.install.stats.specialValue
                  elif turret.install.stats.special == ids.S_INERTIA:
                      self.inertiaMod = turret.install.stats.specialValue
                  elif turret.install.stats.special == ids.S_SAIL:
                      solarSailEfficiency += turret.install.stats.specialValue
                  elif turret.install.stats.special == ids.S_JAMMER and game.tick%(config.fps/2) == 5:
                       for obj in game.objects.getWithin( self, turret.install.stats.specialValue ):
                           if isinstance( obj, Missile ):
                               obj.loseTarget( game )
                  if turret.install.stats.darkExtractor:
                      darkExtractorEfficiency += turret.install.stats.darkExtractor
                  if turret.install.stats.darkEngine:
                      darkEngineEfficiency += turret.install.stats.darkEngine
                  if turret.install.stats.hullBonusVsEnergy:
                      self.hullVsEnergy += turret.install.stats.hullBonusVsEnergy
                  if turret.install.stats.shieldBonusVsMass:
                      self.shieldVsMass += turret.install.stats.shieldBonusVsMass
                             
        if nebulaOreSum:
            self.addOreToProcess( nebulaOreSum )  
     #     print self.inertiaMod
                      

        # ships
        hangarSpace = self.getHangarSpace()
        count = self.getHangarUse( game )

        for k,b in self.shipyards.iteritems():
         if b.building and count+game.stats[ k ].hangarSpaceNeed<= hangarSpace: #count < self.getMaxShips():
            b.build = b.build+self.getBuildRate()
            if b.build >= b.buildCost:
                ship = buildShip( self.player, game.stats[ k ], 0, 0, flagship=self )
                b.docked.append( ship )

                count = count + game.stats[ k ].hangarSpaceNeed
                if self.canBuild( game, k ):
                   self.buildShip( game, k )
                else:
                   b.building = False

        # missiles
        for k in self.missiles:
          b = self.missiles[ k ]
          if b.building and count+game.stats[ k ].hangarSpaceNeed<= hangarSpace: #count < self.getMaxMissiles():
            b.build = b.build+self.getBuildRate()
            if b.build >= b.buildCost:
                b.amount = b.amount+1
                count = count + game.stats[ k ].hangarSpaceNeed
                if self.canBuild( game, k ):
                   self.buildMissile( game, k )
                else:
                   b.building = False

        # resources
        for r in self.oreProcess:
            r.pos = r.pos + self.getBuildRate()
            if r.pos >= self.processLength:
                self.oreProcess.remove( r )
                self.ore = min(self.ore + r.amount,self.stats.maxOre)

        # energy
        solarEnergyPotential = 0
        absorbtion = 0
        distFromSun = 1000000
        
        absorbtion = self.getEnergyAbsorbtion()
        for obj in game.astres:
            if isinstance( obj, Sun ):
                dist = distBetweenObjects( self, obj )
                if dist < obj.stats.energyRadius:
                    solarEnergyPotential = solarEnergyPotential+(obj.stats.energyRadius-dist)/obj.stats.energyRadius*obj.stats.maxEnergy
                if dist < distFromSun:
                    distFromSun = dist
        if not self.inNebula: # RULE sun blocked out in the nebula
            self.energy = min(self.energy + absorbtion * solarEnergyPotential,self.stats.maxEnergy)
        
        darkEnergyPotential = sqrt( max( 0, (distFromSun-12000)/150000) )
        if darkEnergyPotential:
        #    print distFromSun, darkEnergyPotential
            self.energy = min(self.energy + darkEnergyPotential*darkExtractorEfficiency, self.stats.maxEnergy)
                
        
        # thrust
        ## solar sails and dark engines
        if darkEngineEfficiency:
            print darkEngineEfficiency, darkEnergyPotential
        self.thrustBoost = solarSailEfficiency*solarEnergyPotential + darkEnergyPotential*darkEngineEfficiency
        
        # repairs
        if self.repairing and self.ore >= self.getHullRepairRate(): #self.lastRepairsAt+self.repairDelay <= game.tick and self.ore > 0:
            if self.hull < self.stats.maxHull:
                self.hull = self.hull + self.getHullRepairRate()
                self.ore = self.ore - self.getHullRepairRate()
                self.repairDelay = game.tick

            for sy in self.shipyards.values():
              for ship in sy.docked: # self.dockedFighters + self.dockedHarvesters:
                if self.ore > 0 and ship.hull < ship.stats.maxHull:
                    ship.hull = ship.hull + self.getHullRepairRate()
                    self.ore = self.ore - self.getHullRepairRate()
                    self.repairDelay = game.tick
 
        if self.inNebula: # RULE nebula drains shield
            self.shield = self.shield*0.99
        else:
          if self.charging:
            if self.shield < self.stats.maxShield and self.energy >= self.getShieldRegenerationRate():
                self.shield = self.shield + self.getShieldRegenerationRate()
                self.energy = self.energy - self.getShieldRegenerationRate()
         # self
         # fighters

        (ao, ro, ag) = ShipWithTurrets.doTurn( self, game )
        (ao1, ro1, ag1) = JumperShip.doTurn( self, game )
        (ao, ro, ag) = (ao+ao1, ro+ro1, ag+ag1)

        ## update value tu civilians
        if game.tick%config.fps==3:
          value = 1000
          for turret in self.turrets:
            if turret.install:
                if turret.install.stats.special == ids.S_NUKE:
                    value -= 500
                elif turret.install.stats.special == ids.S_REACTOR:
                    value -= 200
                elif turret.install.stats.special == ids.S_CIVILIAN:
                    value += 500
            if turret.weapon:
                value += (turret.weapon.stats.energyDamage + turret.weapon.stats .massDamage)*turret.weapon.stats.freqOfFire/10
          if value <= 0:
            self.civilianValue = 1
          else:
            self.civilianValue = value
            
        if self.player and (int(self.ore) != int(oldOre) or int(self.energy) != int(oldEnergy)):
            if isinstance( self.player, Human ) or not game.tick%config.fps: # Performance optimization, in favor of human players
                for turret in self.turrets:
                    turret.updateBuildingOptionsPossibles()
                    
        if self.selfDestructCommand:
            # get explosion radius
            radius = self.stats.maxRadius
            for turret in self.turrets:
                if turret.install and turret.install.stats.special == ids.T_GENERATOR:
                    radius += turret.install.stats.specialValue

            # die and explode
            (ao1, ro1, fxs1 ) =  self.die( game )
            (ao,ro,ag) = (ao+ao1, ro+ro1, ag+fxs1 )
            ag.append( GfxExplosion( (self.xp,self.yp), radius, sound=ids.S_EX_NUKE ) )

            # hit ships in explosion range
            maxDamage = 1000
            explode( self, game, radius+1000, energyDamage=0, massDamage=maxDamage, pulseLength=0, sender=self.player, deadlyToSelf=False, sound=ids.S_EX_PULSE )
                
        return (ao,ro,ag)

    # override Jumper default
    def getJumpChargeDelay( self ):
        return self.stats.jumpChargeDelay
    jumpChargeDelay = property( fget=getJumpChargeDelay )

    # override Jumper default
    def getJumpRecoverDelay( self ):
        return self.stats.jumpRecoverDelay
    jumpRecoverDelay = property( fget=getJumpRecoverDelay )

    # override Jumper default
    def getJumpCost( self ):
        return self.stats.jumpEnergyCost

    def canJump( self, game ):
        can = JumperShip.canJump( self, game )

        if can and (self.jumping \
                    or ( not self.jumpRecover \
                         and self.energy >= self.stats.jumpEnergyCost ) ):
            return True
        else:
            return False

    def jump( self, (xd, yd), game  ):
        if self.canJump( game ):
          if distBetween( (self.xp, self.yp), (xd, yd) ) > self.getRadarRange():
            for k in self.shipyards:
              for s in self.shipyards[k].away: # self.awayFighters + self.awayHarvesters:
                self.removeShip( s )
                s.flaghsip = None

        return JumperShip.jump( self, (xd, yd), game )

    def delayedJump( self, (xd,yd) ):
        wasJumping = self.jumping

        JumperShip.delayedJump( self, (xd, yd) )

        if not wasJumping and self.jumping:
            self.energy = self.energy - self.getJumpCost()

    def emergencyJump( self ):
        self.energy = self.energy - self.getJumpCost()
        self.jumping = ((1-2*random())*config.universeWidth, (1-2*random())*config.universeHeight)
    
    def addOreToProcess( self, amount ):
      #  self.oreProcess[ 0 ] += 
         self.oreProcess.append( OreBatch( amount ) )


    def addToHangar( self, ship, game ): # TODO add space check
        ship.enterHangar()
        ship.dockedAt = game.tick
        if self.shipyards.has_key( ship.stats.img ) \
         and ship in self.shipyards[ ship.stats.img ].away:
            self.shipyards[ ship.stats.img ].away.remove( ship )
            self.shipyards[ ship.stats.img ].docked.append( ship )
        else:
            self.guestDocked.append( ship )
       #     print "warning: addToHangar: ship not in away"
       # self.shipyards[ ship.stats.img ].docked.append( ship )
        if ship.stats.buildAsHint == "harvester":
            if ship.ore > 0:
                self.addOreToProcess( ship.ore )
                ship.ore = 0
        elif ship.stats.buildAsHint == "builder" or ship.stats.buildAsHint == "transporter":
            if ship.ore > 0:
                self.ore = min( self.ore+ship.ore, self.stats.maxOre )
                ship.ore = 0

    def launch( self, ship, game ):
        if ship.stats.buildAsHint in ( "builder", "transporter" ):
            if self.ore > 0 \
             and not ship in self.guestDocked:
                amount = min( ship.stats.maxOre-ship.ore, self.ore )
                ship.ore += amount
                self.ore -= amount

        if ship in self.guestDocked:
            self.guestDocked.remove( ship )
        else:
            self.shipyards[ ship.stats.img ].docked.remove( ship )
            self.shipyards[ ship.stats.img ].away.append( ship )

    def getRadarRange( self ):
        if self.energy < 10:
            radarRange = 100
        else:
            radarRange = self.stats.radarRange
            for turret in self.turrets:
                if turret.install and turret.activated and turret.install.stats.special == ids.S_RADAR:
                    radarRange = radarRange+turret.install.stats.specialValue

            if self.inNebula: # RULE nebula reduces radar range 
                radarRange = radarRange/4

        return radarRange

    def getEnergyAbsorbtion( self ):
        absorbtion = 1
        for turret in self.turrets:
            if turret.install and turret.activated and turret.install.stats.solar:
                absorbtion = absorbtion+turret.install.stats.solar
        return absorbtion

    def getShieldRegenerationRate( self ):
        return 0.1

    def getHullRepairRate( self ):
        return 0.05*self.getBuildRate()

    def getHangarSpace( self ):
        space = self.stats.hangarSpace
        for turret in self.turrets:
            if turret.install and turret.activated and turret.install.stats.special == ids.S_HANGAR:
                space = space+turret.install.stats.specialValue
        return space

    def getHangarUse( self, game ):
        space = 0
        for missile in self.missiles:
            space = space+self.missiles[missile].amount*game.stats[ missile ].hangarSpaceNeed

        for ship in self.shipyards:
            space = space+self.shipyards[ship].getCount()*game.stats[ ship ].hangarSpaceNeed

        return space



    def die( self, game ):
        (ao,ro,ag) = Ship.die(self, game)
        
        for k,shipyard in self.shipyards.iteritems():
            for docked in shipyard.docked:
                docked.alive = False
                   
        return (ao,ro,ag)

    def removeShip( self, ship ):
        ship.ai.flagship = None
        if self.shipyards.has_key( ship.stats.img ):
            if ship in self.shipyards[ship.stats.img].away:
                self.shipyards[ship.stats.img].away.remove( ship )
            if ship in self.shipyards[ship.stats.img].docked:
                self.shipyards[ship.stats.img].docked.remove( ship )


    def canBuildTurret( self, turret, toBuild ):
        if toBuild:
            oreFlow = -1*toBuild.oreCostToBuild
            energyFlow = -1*toBuild.energyCostToBuild

            if turret.building:
                oreFlow += turret.building.oreCostToBuild
                energyFlow += turret.building.energyCostToBuild

            return self.ore + oreFlow >= 0 and self.energy + energyFlow >= 0
        else: # destroy turret
            return True

    def buildTurret( self, turret, toBuild ):

        if self.canBuildTurret( turret, toBuild ):
            if turret.building: # already building something
                self.ore = self.ore+turret.building.oreCostToBuild
                self.energy = self.energy+turret.building.energyCostToBuild

            turret.ai = None
            turret.weapon = None
            turret.install = None

            turret.building = toBuild
            turret.rr = turret.stats.defaultAngle

            if toBuild:
                self.ore = self.ore-toBuild.oreCostToBuild
                self.energy = self.energy-toBuild.energyCostToBuild

                turret.buildCost = toBuild.timeToBuild # oreCostToBuild
                turret.build = 0
                
            turret.updateBuildingOptions()

    def destroyTurret( self, turret ):
        turret.weapon = None

    def buildShip( self, game, toBuild, switch=False ):
        if switch and self.shipyards[ toBuild ].building:
            self.shipyards[ toBuild ].building = False
            self.energy = self.energy+game.stats[ toBuild ].energyCostToBuild
            self.ore = self.ore+game.stats[ toBuild ].oreCostToBuild
        elif self.canBuild( game, toBuild ):
            self.shipyards[ toBuild ].building = True
            self.shipyards[ toBuild ].build = 0
            self.shipyards[ toBuild ].buildCost = game.stats[ toBuild ].timeToBuild
            self.energy = self.energy-game.stats[ toBuild ].energyCostToBuild
            self.ore = self.ore-game.stats[ toBuild ].oreCostToBuild

    def buildMissile( self, game, toBuild, switch=False ):
        if switch and self.missiles[ toBuild ].building:
            self.missiles[ toBuild ].building = False
            self.energy = self.energy+game.stats[ toBuild ].energyCostToBuild
            self.ore = self.ore+game.stats[ toBuild ].oreCostToBuild
        elif self.canBuild( game, toBuild ):
            self.missiles[ toBuild ].building = True
            self.missiles[ toBuild ].build = 0
            self.missiles[ toBuild ].buildCost = game.stats[ toBuild ].timeToBuild
            self.energy = self.energy-game.stats[ toBuild ].energyCostToBuild
            self.ore = self.ore-game.stats[ toBuild ].oreCostToBuild

    def canBuild( self, game, toBuild ):
        # TODO standardize with canBuildTurret
        return self.energy >= game.stats[ toBuild ].energyCostToBuild \
          and self.ore >= game.stats[ toBuild ].oreCostToBuild

    def launchMissile( self, type, (x,y) ):
        self.missiles[ type ].target = (x,y)

    def getBuildRate( self ):
        rate = 1.0 + len( self.civilianShips )*0.3
        return rate

    def hit( self, game, angle, sender, energy=0, mass=0, pulse=False ):

        # RULE when pulsed e = e/3
        if pulse:
            self.energy = self.energy/3

        return ShipWithTurrets.hit( self, game, angle, sender, energy, mass, pulse )

    def selfDestruct( self, game ):
        self.selfDestructCommand = True
        
    def getCryptionStrength( self ):
        cryption = 0
        for turret in self.turrets:
            if turret.install and turret.activated:
                cryption += turret.install.stats.cryption
        return cryption
    cryptionStrength = property( fget=getCryptionStrength )

class OrbitalBase( FlagShip ):
    def __init__( self, player, stats, ai, xp, yp, zp=0, ori=0.0, xi=0, yi=0, zi=0, ri=0, thrust=0 ):
        FlagShip.__init__( self, player, stats, ai, xp, yp, zp, ori, xi, yi, zi, ri, thrust )
        self.headed = False
        self.inertiaControl = False

class WorkerShip( ShipWithTurrets ):
    def __init__( self, player, stats, ai, xp, yp, zp=0, ori=0.0, xi=0, yi=0, zi=0, ri=0, thrust=0 ):
        self.player = player
        ShipWithTurrets.__init__( self, player, stats, ai, xp, yp, zp, ori, xi, yi, zi, ri, thrust )
        self.ore = 0
        
        if self.stats.turretType:
            for turret in self.turrets:
                turret.ai = AiTargeterTurret()
                turret.install = TurretInstall( self.stats.turretType )

class HarvesterShip( WorkerShip ):
    def __init__( self, player, stats, ai, xp, yp, zp=0, ori=0.0, xi=0, yi=0, zi=0, ri=0, thrust=0 ):
        WorkerShip.__init__( self, player, stats, ai, xp, yp, zp, ori, xi, yi, zi, ri, thrust )

        self.harvestedInRange = False

    def doTurn( self, game ):
        if self.ai.working and self.orbiting:
            self.ore = min(self.ore + 0.1, self.stats.maxOre )

        return WorkerShip.doTurn( self, game )

class BuilderShip( WorkerShip ):
    def __init__( self, player, stats, ai, xp, yp, zp=0, ori=0.0, xi=0, yi=0, zi=0, ri=0, thrust=0 ):
        WorkerShip.__init__( self, player, stats, ai, xp, yp, zp, ori, xi, yi, zi, ri, thrust )

    def doTurn( self, game ):
        if self.ai.working and self.orbiting: # TODO ai
            amount = 0.2
            self.ore = max(self.ore - amount, 0 ) # TODO builder stats
            self.ai.working.work( amount )
         #   print "builder working", self.ore, self.ai.working.buildEffort

        return ShipWithTurrets.doTurn( self, game )


class Frigate( ShipWithTurrets, JumperShip ):
    """ai -> AiFrigateCaptain
       stats -> FrigateStats"""
    def __init__( self, player, stats, ai, xp=0, yp=0, zp=-2, ori=0, xi=0, yi=0, zi=0, ri=0, thrust=0 ):
        self.player = player
        ShipWithTurrets.__init__( self, player, stats, ai, xp, yp, zp, ori, xi, yi, zi, ri, thrust )
        JumperShip.__init__( self )

    # This is a hack to allow use of turrets TODO 
    ore = property( fget=lambda self: 1000 )
    energy = property( fget=lambda self: 1000 )

    def doTurn( self, game ):
        (addedObjects0, removedObjects0, addedGfxs0) = ShipWithTurrets.doTurn( self, game )
        (addedObjects1, removedObjects1, addedGfxs1) = JumperShip.doTurn( self, game )
        return (addedObjects0+addedObjects1, 
                removedObjects0+removedObjects1, 
                addedGfxs0+addedGfxs1)

class Scaffolding( Ship ):
    def __init__( self, stats, xp, yp, player, build ):
        ori = 2*pi*random()
        zp = -3
        Ship.__init__( self, stats, None, xp, yp, zp, ori )

        self.player = player
        
        self.building=build
        self.buildEffort = 0

    #    print "Scaffolding created"

    def doTurn( self, game ):    
        ( ao, ro, ag ) = Ship.doTurn( self, game )

        # TODO remove when builders are available
       # self.buildEffort += 0.1

        # act on build effort
        # assumes self.building and self.player
        if self.buildEffort >= self.building.oreCostToBuild:
            ori = 2*pi*random()
            ao.append( buildShip( self.player, self.building, self.xp, self.yp, ori=ori )  ) # build target

            self.alive = False
            ro.append( self )

            explosionRange = max( self.stats.maxRadius, self.building.maxRadius )
            ag.append( GfxExplosion( (self.xp,self.yp), explosionRange, sound=ids.S_EX_FIRE ) )

        return ( ao, ro, ag )

    def work( self, contribution ):
        self.buildEffort += contribution

#from stats import *
def buildShip( player, stats, xp, yp, ori=0, flagship=None ):
    print "building ", stats
    if stats.buildAsHint == "frigate":
        return Frigate( player, stats, AiEscortFrigate( player ), xp, yp, ori=ori )
    elif stats.buildAsHint == "base":
        return OrbitalBase( player, stats, AiGovernor( player ), xp, yp, ori=ori, ri=choice([0.008,-0.008]) )
    elif stats.buildAsHint == "harvester":
        return HarvesterShip( player, stats, AiPilotHarvester(flagship), xp,yp,0, 4, 0.0,0.0,0.0, 0)
    elif stats.buildAsHint == "builder":
        return BuilderShip( player, stats, AiPilotBuilder(flagship), xp,yp,0, 4, 0.0,0.0,0.0, 0)
    elif stats.buildAsHint == "transporter":
        return BuilderShip( player, stats, AiPilotTransporter(flagship), xp,yp,0, 4, 0.0,0.0,0.0, 0)
    elif stats.buildAsHint == "single weapon ship":
        return ShipSingleWeapon( player, stats, AiPilotFighter(flagship), xp,yp,0, 4, 0.0,0.0,0.0, 0)
    else:
        raise Warning( "Unknown ship in ships.buildShip for stats and id:", stats, stats.id )

