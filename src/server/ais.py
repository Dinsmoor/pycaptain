from random import randint, random, choice
from time import time
from math import pi, fabs, cos, sin

from common.utils import * 
from objects import Object, Asteroid, Sun, Nebula
from ships import Ship
from weapons import *
from players import Human
from common import config
from common import ids
# from ships import *

class AiPilot:
    def __init__(self):
        self.stance = 0
        self.goingTo = False
        self.dockingTo = None
        self.dockedTo = False
        self.attacking = False
        self.idle = True
        self.evading = False

    def goTo(self, ship, dest, destOri=0, orbitAltitude=2):
        """main goTo logic. 
Can change self.goingTo. May change self.attacking and self.dockingTo."""
        ship.orbiting = False
        self.goingTo = dest

        if isinstance( dest, Object ):
          if not dest.stats.orbitable:
            dest = (dest.xp, dest.yp)
          else:
      #  elif isinstance( dest, Object ) and dest.stats.orbitable:
            angle = angleBetweenObjects( dest, ship )
     #       print dest.stats.maxRadius*orbitAltitude
            dist = dest.stats.maxRadius*orbitAltitude # +ship.stats.maxRadius
            dest = (dest.xp+cos( angle )*dist, dest.yp+sin( angle )*dist)
        #    if ship.player:
      #      print dist

        dist = distBetween( (ship.xp, ship.yp), dest )
        if not isinstance( ship.player, Human ):
          if dist > 2000:
            if self.attacking:
                self.attacking = False
            if self.dockingTo:
                self.dockingTo = None
            return None

        if dist < max( 8, ship.stats.maxRadius/4 ):
            if ship.xi > 0 or ship.yi > 0:
	        ship.thrust = -1*ship.stats.maxReverseThrust
            else:
	        ship.thrust = 0

            if fabs( ship.ri ) >= 0.0005:
                if ship.ri > 0:
                    ship.rg = -0.3*ship.stats.maxRg
                else:
                    ship.rg = 0.3*ship.stats.maxRg
 
            if isinstance( self.goingTo, Object ) and self.goingTo.stats.orbitable:
                ship.orbiting = self.goingTo

            self.goingTo = False
            self.evading = False
            self.idle = True
            
       #     self.idle( ship )
        else:
            destAngle = angleBetween( (ship.xp, ship.yp), dest )
            angle = angleDiff( destAngle, ship.ori )

            absAngle = fabs( angle )
            if absAngle >  ship.stats.maxRg/5: # 0.08:
                ship.rg = ship.stats.maxRg*8*angle/pi

                if ship.ai and ship.ai.attacking:
                    ship.rg += (2-random())*(0.1*ship.stats.maxRg)

                if ship.rg > ship.stats.maxRg:
                    ship.rg = ship.stats.maxRg
                if ship.rg < -1*ship.stats.maxRg:
                    ship.rg = -1*ship.stats.maxRg
            elif ship.ai and ship.ai.attacking:
                ship.rg += (2-random())*(0.3*ship.stats.maxRg)

                if ship.rg > ship.stats.maxRg:
                    ship.rg = ship.stats.maxRg
                if ship.rg < -1*ship.stats.maxRg:
                    ship.rg = -1*ship.stats.maxRg


            maxThrust = ship.stats.maxThrust+ship.thrustBoost
            if dist > maxThrust*100:
	    	ship.thrust = maxThrust
            else:
	    	ship.thrust = maxThrust*(dist/(maxThrust*100)) - 0.8 * absAngle * maxThrust / pi 
                if ship.thrust < 0 and ship.thrust < -1*ship.stats.maxReverseThrust:
                    ship.thrust = -1*ship.stats.maxReverseThrust

            self.idle = False


    def doTurn( self, ship, game ):
      if ship.pulsedUntil < game.tick:
        removedObjects = []

        if self.goingTo:
            self.goTo( ship, self.goingTo )

        if self.dockingTo and not self.dockingTo.alive:
            self.dockingTo = None

        if self.idle:
            if self.dockingTo:
                if ship.zp >= self.dockingTo.zp \
                  and areOver( ship, self.dockingTo ): # somewhere over the mothership
                    self.evade( ship, self.dockingTo, self.dockingTo.stats.maxRadius * 1.5 )
                elif distLowerThanObjects( ship, self.dockingTo, min(20, self.dockingTo.stats.maxRadius/3) ): #distBetweenObjects( ship, self.dockingTo ) < min(20, self.dockingTo.stats.maxRadius / 3): # ready to dock
                    self.dockingTo.addToHangar( ship, game )
                    removedObjects.append( ship )
                    self.dockedTo = self.dockingTo
                    self.dockingTo = False
                    self.idle = True
                else: # away
                    ship.zp = self.dockingTo.zp-10
                    self.goTo( ship, self.dockingTo )

        if self.idle and ship.inertiaControl:
            if fabs( ship.ri ) >= 0.0005:
                if ship.ri > 0:
                    ship.rg = -0.1*ship.stats.maxRg
                else:
                    ship.rg = 0.1*ship.stats.maxRg
       #     if fabs( ship.xi ) >= 0.05
            

        return ( [], removedObjects, [] )
      else:
        return ( [], [], [] )
    #    if self.idle:
    #    if self.intercepting:
                	

  #  def atDestination(self, ship):
  #      if self.dockingTo and distBetweenObjects( self.ship, self.dockingTo ) < self.dockingTo.stats.maxRadius / 2:
  #          self.dockedTo = self.dockingTo

    def evade( self, ship, target, dist ):
        self.idle = True
        self.dockedTo = False
        self.dockingTo = False
        self.evading = True
        angle = random()*2*pi
     #   dist = self.dockingTo.stats.radiusAt( angle ) * 1.5
        dest = ( target.xp+cos(angle)*dist, target.yp+sin(angle)*dist )
        self.goTo( ship, dest )

    def dock( self, ship, motherShip, game ):
        self.goingTo = None
        self.idle = True
        self.dockedTo = False
        self.attacking = False
        self.evading = False
        self.dockingTo = motherShip

        if ship.zp >= self.dockingTo.zp: # must go under the ship
     #       for obj in utils.mY # TODO skipped a lot of steps
     #     and not areOver( ship, self.dockingTo ):
            ship.zp = self.dockingTo.zp - 1    #self.evade( ship, self.dockingTo, self.dockingTo.stats.maxRadius * 1.5 )

    def attack( self, ship, target ):
        self.idle = True
        self.goingTo = False
        self.evading = False
        self.attacking = target

    def stop( self, ship ):
        self.idle = True
        self.goingTo = (ship.xp+ship.xi*10,ship.yp+ship.yi*10)
        self.attacking = False
        self.evading = False

  #  def goToOrbit( self, target ):
    def died( self, ship, game ):
        pass

    def getRandomGuardPosition(self, ship, target, closeness ):
        dist = target.stats.maxRadius*closeness
        diff = 6 * config.fps * target.stats.maxThrust / ship.stats.maxThrust
        return self.getRandomPosition( ship, (target.xp+diff*target.xi, target.yp+diff*target.yi), dist )

    def getRandomPosition(self, ship, destination, radius ):
        x = destination[0]
        y = destination[1]
        return ( randint(int(x-radius),int(x+radius)), 
                 randint(int(y-radius),int(y+radius)) )

    def hitted( self, ship, game, angle, sender, energy, mass, pulse ):
        pass

    ### builders and scaffoldings
    def hasScaffoldingInSight( self, ship, game, dist=None ):
        if not dist:
            dist = self.getSearchRange( ship )

        for x in game.objects.getAccording( ship.pos, dist=dist, 
                 func=lambda x: x.stats.buildAsHint == "scaffolding" and x.player == ship.player ):
            return True

        return False

    def getClosestScaffolding( self, ship, game, dist=None ):
        if not dist:
            dist = self.getSearchRange( ship )

        return game.objects.getClosestAccording( ship, dist, 
                 func=lambda x: x.stats.buildAsHint == "scaffolding" and x.player == ship.player )

    ### harvesters asteroids
    def hasAsteroidsInSight( self, ship, game, dist=None ):
        if not dist:
            dist = self.getSearchRange( ship )

        for x in game.harvestables.getWithinArea( ship, dist ):
            return True

        return False
    
    def getClosestAsteroid( self, ship, game, dist=None ):
        if not dist:
            dist = self.getSearchRange( ship )

        return game.harvestables.getClosestAccording( ship, dist )

    ### transport
    def hasShipInNeedInSight( self, ship, game, dist=None ):
        if not dist:
            dist = self.getSearchRange( ship )

        for x in game.objects.getAccording( ship.pos, dist=dist, # , "frigate"
                           func=lambda x: x.stats.buildAsHint in ("flagship", "base" ) \
                           				  and x != ship \
                                          and x.player == ship.player \
                                         # and x.ore < self.flagship.ore \
                                          and x.ore < 0.8*x.stats.maxOre ):
            return True

        return False

    def getRandomShipInNeed( self, ship, game, dist=None ):
        if not dist:
            dist = self.getSearchRange( ship )

        inNeedOfOre = [ x for x in game.objects.getAccording( ship.pos, dist=dist, # , "frigate"
                           func=lambda x: x.stats.buildAsHint in ("flagship", "base" ) \
                           				  and x != ship \
                           				  and self.caresAboutShipNeeds( ship, x ) \
                                          and x.player == ship.player \
                                         # and x.ore < self.flagship.ore \
                                          and x.ore + ship.ore <= x.stats.maxOre ) ]
        
        # TODO sort in order of need and/or proximity
        #for inNeed in inNeedOfOre:
        if len(inNeedOfOre)>0:
            return choice(inNeedOfOre)
        else:
            return None

    def getNeediestShip( self, ship, game, dist=None ):
        if not dist:
            dist = self.getSearchRange( ship )

        inNeedOfOre = [ x for x in game.objects.getAccording( ship.pos, dist=dist, # , "frigate"
                           func=lambda x: x.stats.buildAsHint in ("flagship", "base" ) \
                           				  and x != ship \
                           				  and self.caresAboutShipNeeds( ship, x ) \
                                          and x.player == ship.player \
                                         # and x.ore < self.flagship.ore \
                                          and x.ore + ship.ore <= x.stats.maxOre ) ]
        
        # TODO sort in order of need and/or proximity
        #for inNeed in inNeedOfOre:
        if len(inNeedOfOre)>0:
        
            mostInNeed = inNeedOfOre[0]
            lastNeed = 10 * mostInNeed.ore / mostInNeed.stats.maxOre
            for s in inNeedOfOre[1:]:
                if 10 * s.ore / s.stats.maxOre < lastNeed:
                    mostInNeed = s
                    lastNeed = 10 * mostInNeed.ore / mostInNeed.stats.maxOre
                   
            return mostInNeed
        else:
            return None
            
    def caresAboutShipNeeds( self, ship, otherShip ):
    	return True 

    def getSearchRange( self, ship ):
        return ship.stats.radarRange

class AiPilotFaction( AiPilot ):
    def __init__(self):
        AiPilot.__init__(self)
        self.hittedAt = -1000

    def doTurn( self, ship, game):
        pass

    def hitted( self, ship, game, angle, sender, energy, mass, pulse ):
#        print "hitted"
        AiPilot.hitted( self, ship, game, angle, sender, energy, mass, pulse )
        self.hittedAt = game.tick
        if sender and not self.attacking and game.getRelationBetween( ship.player, sender )<0:
            self.attacking = game.objects.getClosestAccording( ship, 2000, 
	func=lambda obj: isinstance( obj, Ship ) and obj.player and obj.player == sender )
                    

    def needsHelp( self, game ):
        return self.hittedAt > game - config.fps*10

class AiPilotDefense( AiPilotFaction ):
    def __init__(self, defended, radius ):
        AiPilotFaction.__init__(self)
        self.defended = defended
        self.radius = int(radius)
        self.lastDestSetAt = -1000

    def doTurn( self, ship, game):
        if self.attacking and (not self.attacking.alive or self.attacking.dockedTo):
            self.attacking = None

        ( ao, ro, ag ) = AiPilot.doTurn( self, ship, game )

        if not self.attacking and self.idle and not self.dockingTo and game.tick%(0.5*config.fps)==2:
            self.attacking = game.objects.getClosestAccording( ship, 1000, 
	func=lambda obj: isinstance( obj, Ship ) and obj.alive and obj.player and game.getRelationBetween( ship.player, obj.player ) < 0 )

        if not self.dockingTo and not self.attacking and (self.idle or self.lastDestSetAt<game.tick-config.fps*5 ):
            self.goTo( ship, self.setNewDest( ship, game) )

        if not self.dockingTo and self.attacking:
            if not self.evading and distLowerThanObjects( ship, self.attacking, ship.weapon.stats.minRange+self.attacking.stats.maxRadius ):
                self.evade( ship, self.attacking, ship.weapon.stats.maxRange*0.9+self.attacking.stats.maxRadius/2 )
            elif self.idle:
                self.goTo( ship, self.attacking )

            if self.attacking and ship.weapon.canFire( ship, game ):
                angle = angleBetweenObjects( ship, self.attacking )
                if ship.ori >= angle - pi/40 \
                  and ship.ori <= angle + pi/40: # TODO
                    if distLowerThanObjects( ship, self.attacking, ship.weapon.stats.maxRange+self.attacking.stats.maxRadius ):
                        ( ao1, ro1, ag1 ) = ship.weapon.fire( ship, game, self.attacking )
                        ( ao, ro, ag ) = ( ao+ao1, ro+ro1, ag+ag1 )

        return ( ao, ro, ag)

    def setNewDest(self,ship, game):
        dist = randint( self.radius/2, self.radius)
        angle = 2*pi*random()
        if isinstance( self.defended, Object ):
            (x,y) = (self.defended.xp, self.defended.yp)
        else:
            (x,y) = self.defended
        self.goingTo = ( x+dist*cos(angle), y+dist*sin(angle) )
        self.lastDestSetAt = game.tick
        return self.goingTo

class AiPilotPolice( AiPilotDefense ):
    def __init__( self, defended, radius ):
        AiPilotDefense.__init__(self, defended, radius) 
        self.policingRange = 500

    def doTurn( self, ship, game):
        if not self.attacking and game.tick%(config.fps/2) == 7:         
            self.attacking = game.objects.getClosestAccording( ship, 1000, 
	func=lambda obj: isinstance( obj, Ship ) and obj.alive and obj.player and game.getRelationBetween( ship.player, obj.player ) < 0 )

            for obj in game.objects.getWithin( ship, self.policingRange ): # game.objects.objects:
                if obj.player and obj.player != ship.player and isinstance( obj.player, Human ) and obj.player.online and obj.ai and obj.ai.attacking and distLowerThanObjects( ship, obj.ai.attacking, self.policingRange ):
                    self.attack( ship, obj )
                    break

        return AiPilotDefense.doTurn( self, ship, game)

class AiPilotOrbiter( AiPilot ):
    pass

class AiPilotFighter( AiPilot ):
    def __init__(self,flagship):
        AiPilot.__init__(self)
        self.flagship = flagship

    def doTurn( self, ship, game ):
      if self.attacking and not self.attacking.alive:
            self.attacking = None

      if not self.flagship and not self.attacking:
        ( ao, ro, ag ) = ship.die( game )
      else:
        ( ao, ro, ag ) = AiPilot.doTurn( self, ship, game )


        if not self.attacking and self.idle and not self.dockingTo and self.flagship.ai.attacking:
            self.attacking = game.objects.getClosestAccording( ship, 1000, 
	func=lambda obj: isinstance( obj, Ship ) and obj.alive and obj.player and game.getRelationBetween( ship.player, obj.player ) < 0 )

        if not self.dockingTo and self.idle and not self.attacking:
            self.goTo( ship, self.getRandomGuardPosition(ship, self.flagship, 1.5) )

        if not self.dockingTo and self.attacking:
            if not self.evading and distLowerThanObjects( ship, self.attacking, ship.weapon.stats.minRange+self.attacking.stats.maxRadius ):
                self.evade( ship, self.attacking, ship.weapon.stats.maxRange*0.9+self.attacking.stats.maxRadius/2 )
            elif self.idle:
                self.goTo( ship, self.attacking )

            if self.attacking and ship.weapon.canFire( ship, game ):
                angle = angleBetweenObjects( ship, self.attacking )
                if ship.ori >= angle - pi/40 \
                  and ship.ori <= angle + pi/40: # TODO
                    if distLowerThanObjects( ship, self.attacking, ship.weapon.stats.maxRange+self.attacking.stats.maxRadius ):
                        ( ao1, ro1, ag1 ) = ship.weapon.fire( ship, game, self.attacking )
                        ( ao, ro, ag ) = ( ao+ao1, ro+ro1, ag+ag1 )

      return ( ao, ro, ag)

    #def getRandomGuardPosition(self, ship, target, closeness ):
   #     dist = target.stats.maxRadius*closeness
  #      return (randint(int(target.xp-dist),int(target.xp+dist)), randint(int(target.yp-dist),int(target.yp+dist)) )
#
 #   def getRandomGuardPosition(self, ship, target, closeness ):
 #       dist = target.stats.maxRadius*closeness
#        return (randint(int(target.xp-dist),int(target.xp+dist)), randint(int(target.yp-dist),int(target.yp+dist)) )

    def died( self, ship, game ):
        if self.flagship:
            self.flagship.removeShip( ship )


class AiShipWithTurrets( AiPilot ):
    """AI for ships with turrets"""
    def __init__(self,player):
        self.player = player # TODO remove? useless as of now
        AiPilot.__init__(self)

    def doTurn( self, ship, game):
        if self.attacking and not self.attacking.alive:
            self.attacking = None

        addedObjects0 = []
        removedObjects0 = []
        addedGfxs0 = []

        if self.attacking:
            pass
        elif game.tick%(config.fps/2)==9: # no target
            
            bestObj = game.objects.getClosestAccording( ship, 500, # TODO, make dynamic as before with ship.stats.radarRange, 
	func=lambda obj: isinstance( obj, Ship ) and obj.alive and obj.player and obj.player != ship.player and game.getRelationBetween( ship.player, obj.player ) < 0 )

            if bestObj:
                self.attack( ship, bestObj )#attacking = bestObj

        # turrets / weapons
        for turret in ship.turrets:
            if turret.ai and turret.activated: # if turret is armed
                (ao, ro, ag) = turret.ai.doTurn( ship, turret, game, self.attacking)
                addedObjects0 = addedObjects0 + ao
                removedObjects0 = removedObjects0 + ro
                addedGfxs0 = addedGfxs0 + ag

        (addedObjects1, removedObjects1, addedGfxs1) = AiPilot.doTurn( self, ship, game )
        return (addedObjects0+addedObjects1, removedObjects0+removedObjects1, addedGfxs0+addedGfxs1)

    def stop(self, ship):
        AiPilot.stop( self, ship )
        for t in ship.turrets:
          if t.ai:
            t.ai.target = None

    def attack( self, ship, target ):
        self.idle = True
        self.goingTo = False
        self.attacking = target

class AiEscortFrigate( AiShipWithTurrets ):
    def __init__(self,player):
        AiShipWithTurrets.__init__(self,player)
        self.maxDistWithEscorted = 1000
        self.lastDestSetAt = 0

    def doTurn( self, ship, game ):
        (addedObjects, removedObjects, addedGfxs) = AiShipWithTurrets.doTurn( self, ship, game )
        
        # follow flagship
        if ship.player and ship.player.flagship and ship.player.flagship.alive:
            if ship.canJump and not ship.jumping:
                if ship.player.flagship.jumping:
                   if utils.distGreaterThan( (ship.xp,ship.yp), self.player.flagship.jumping, self.maxDistWithEscorted*1.2 ):
                    # jump
                        ship.delayedJump( self.getRandomPosition( ship, self.player.flagship.jumping, self.player.flagship.stats.maxRadius*3 ), config.fps*(1+3*random()) )
                elif utils.distGreaterThanObjects( ship, ship.player.flagship, self.maxDistWithEscorted ):
                    # jump
                    ship.delayedJump( self.getRandomGuardPosition( ship, self.player.flagship, 2 ), config.fps*(1+3*random()) )

            # fight
            # must have a target guide to force turrets to find targets
            if not self.attacking and game.tick%(0.5*config.fps)==4:
                self.attacking = game.objects.getClosestAccording( ship, 1000, 
	    func=lambda obj: isinstance( obj, Ship ) and obj.alive and obj.player and game.getRelationBetween( ship.player, obj.player ) < 0 )

            # set guard position
            ## not self.attacking and 
            if (self.idle or self.lastDestSetAt<game.tick-config.fps*10) and \
               not ship.player.flagship.jumping: # 
                self.goTo( ship, self.getRandomGuardPosition( ship, self.player.flagship, 3 ) )
                self.lastDestSetAt = game.tick

        return  (addedObjects, removedObjects, addedGfxs)

class AiCaptain( AiShipWithTurrets ):
    """AI for ships with turrets and shipyards"""
    def __init__(self,player):
        AiShipWithTurrets.__init__(self,player)
        self.launching = {}
        for s in player.race.ships:
            self.launching[ s.img ] = False

    def doTurn( self, ship, game):
        (addedObjects, removedObjects, addedGfxs) = AiShipWithTurrets.doTurn( self, ship, game )

        for k in self.launching:
            if self.launching[ k ] and len( ship.shipyards[ k ].docked ) > 0 and ship.lastLaunchAt + ship.stats.launchDelay < game.tick:
                for s in ship.shipyards[ k ].docked:
                    if s.dockedAt + ship.stats.launchDelay*3 < game.tick:
                        hangar, hangarAngle = choice(ship.stats.hangars)

                        (s.xp,s.yp) = (ship.xp+hangar.dist*cos( hangar.angle ), ship.yp+hangar.dist*sin( hangar.angle ))
                        angle = ship.ori+hangarAngle
                        (s.xi,s.yi) = (5*cos(angle),5*sin(angle))
                        s.ori = angle

                        s.zp = ship.zp-2
                        ship.launch( s, game )

                        addedObjects.append( s )
                        s.ai.evade( s, ship, ship.stats.maxRadius*1.5 )

                        ship.lastLaunchAt = game.tick
                        break

            elif not self.launching[ k ]:
              for s in ship.shipyards[ k ].away:
                s.ai.dock( s, ship, game )


        if ship.lastLaunchAt + ship.stats.launchDelay < game.tick \
         and len(ship.guestDocked) \
         and ship.guestDocked[ 0 ].dockedAt + ship.stats.launchDelay*3 < game.tick:

                s = ship.guestDocked[ 0 ]
            # 
            ## TODO duplicated :(

                hangar, hangarAngle = choice(ship.stats.hangars)

                (s.xp,s.yp) = (ship.xp+hangar.dist*cos( hangar.angle ), ship.yp+hangar.dist*sin( hangar.angle ))
                angle = ship.ori+hangarAngle
                (s.xi,s.yi) = (5*cos(angle),5*sin(angle))
                s.ori = angle

                s.zp = ship.zp-2
                ship.launch( s, game )

                addedObjects.append( s )
                s.ai.evade( s, ship, ship.stats.maxRadius*1.5 )

                ship.lastLaunchAt = game.tick
            

        return (addedObjects, removedObjects, addedGfxs)

    def launchShips(self, ship, game, type ):
        self.launching[ type ] = True
        
    def recallShips(self, ship, game, type ):
        self.launching[ type ] = False
        for s in ship.shipyards[ type ].away: #awayFighters:
            s.ai.dock( s, ship, game )

    def stop(self, ship):
        AiShipWithTurrets.stop( self, ship )
        for k in ship.shipyards:
          if k != ids.S_HARVESTER:
            for s in ship.shipyards[ k ].away:
              s.ai.stop( s )

    def attack( self, ship, target ):
        AiShipWithTurrets.attack( self, ship, target )
        for k in ship.shipyards:
            if k != ids.S_HARVESTER:
                for s in ship.shipyards[ k ].away:
                    if s.ai.attacking != self.attacking:
                        s.ai.attack( ship, self.attacking )

    ### used by player ai
    def manageTurretsUpgrades( self, ship ):
        if self.isSafe( ship ) \
         and ship.ore > 2*ship.stats.maxOre/4: # ore > 3/4
            #print "has 3/4"
            choices = []
            for turret in ship.turrets:
                if not turret.building and turret.install:
                    #print "turret", turret.install
                    for possible in ship.player.race.turrets:
                        #print "p", possible.upgradeFrom
                        if turret.install.stats == possible.upgradeFrom \
                         and possible.weapon \
                         and ship.canBuildTurret( turret, possible ):
                            choices.append( (turret, possible) )

           # print "choices", choices
            if len(choices):
                turret,toBuild = choice( choices )
                ship.buildTurret( turret,toBuild )

    def isSafe( self, ship ):
        return True # default :(

class AiGovernor( AiCaptain ):
    def __init__(self,player):
        AiCaptain.__init__(self,player)

        self.ennemyInSight = []

        self.scaffoldingsInSight = []

    def doTurn( self, ship, game):
        (ao, ro, ag) = AiCaptain.doTurn( self, ship, game )

        if game.tick%config.fps==24:

            ### detect ennemy in sight
            seenThisTurn = []
            for obj in game.objects.getWithinRadius( ship.pos, ship.stats.radarRange ):
                if obj.alive and obj.player and obj.stats.buildAsHint == "flagship" \
                and game.getRelationBetween( ship.player, obj.player ) < 0:

                    seenThisTurn.append( obj )

                    if not obj in self.ennemyInSight:

                        self.ennemyInSight.append( obj )

                        msg = "@uto; enemy in sight from %.2f, %.2f" % (ship.xp/1000.0, ship.yp/1000.0)
                        game.communicationManager.addWideBroadcast( game, ship.player, msg, ship=ship, encryption=1 )

            ### clear unseen enemy from memory
            ennemyToForget = []
            for ship in self.ennemyInSight:
                if not ship in seenThisTurn:
                    ennemyToForget.append( ship )

            for ship in ennemyToForget:
                self.ennemyInSight.remove( ship )

            launch = {}
            recall = {}
            ### manage small ships
            if self.isSafe( ship ):
                ### safe
                launchFighters = False
                recallFighters = True

                ### harvesters
                #recallHarvesters = False
                if ship.ore < ship.stats.maxOre - 1:
                    if ship.noOreCloseAt < game.tick - 15*config.fps: # there may be ore around
                        oreClose = self.hasAsteroidsInSight( ship, game )
                        if not oreClose:
                            ship.noOreCloseAt = tick
                    else:
                        oreClose = False
                        
                    launchHarvesters = oreClose
                else:
                    launchHarvesters = False
                recallHarvesters = not launchHarvesters

                ### builders
                recallBuilders = False
                launchBuilders = False
                if ship.ore > 0:
                    for s in self.scaffoldingsInSight:
                        if s.alive:
                            launchBuilders = True
                            break

                    if not launchBuilders: # no known scaffoldings in sight
                        launchBuilders = self.hasScaffoldingInSight( ship, game )
                    recallBuilders = not launchBuilders
            else:
                ### danger
                launchHarvesters = False
                launchBuilders = False
                launchFighters = True

                recallHarvesters = True
                recallBuilders = True
                recallFighters = False

            if self.hasShipInNeedInSight( ship, game ): # there is need
                launchTransports = ship.ore >= 0.6*ship.stats.maxOre # is wealthy
                recallTransports = ship.ore < 0.2*ship.stats.maxOre # is poor
            else:
                launchTransports = False
                recallTransports = True

            for i in self.launching:
                if game.stats[ i ].buildAsHint == "harvester":
                    if not self.launching[ i ] and launchHarvesters:
                        self.launching[ i ] = True
                    elif self.launching[ i ] and recallHarvesters:
                        self.launching[ i ] = False
                elif game.stats[ i ].buildAsHint == "builder":
                    if not self.launching[ i ] and launchBuilders:
                        self.launching[ i ] = True
                    elif self.launching[ i ] and recallBuilders:
                        self.launching[ i ] = False
                elif game.stats[ i ].buildAsHint == "transporter":
                    if not self.launching[ i ] and launchTransports:
                        self.launching[ i ] = True
                    elif self.launching[ i ] and recallTransports:
                        self.launching[ i ] = False
                else: ## others/combat
                    if not self.launching[ i ] and launchFighters:
                        self.launching[ i ] = True
                    elif self.launching[ i ] and recallFighters:
                        self.launching[ i ] = False

            ### manage turrets
            if self.isSafe( ship ):
                self.manageTurretsUpgrades( ship )

        return (ao, ro, ag)

   # def hitted( self, ship, game, angle, sender, energy, mass, pulse ):
   #     pass

    def goTo(self, ship, dest, destOri=0, orbitAltitude=2):
        pass

    def isSafe( self, ship ):
        return len(self.ennemyInSight) == 0

class AiTurret:
    def __init__( self ):
        self.target = None
        self.attacking = False
        self.rTarget = 0
        self.foundNothingAt = -1000

    def doTurn( self, ship, turret, game, attack):

        pos = ship.getTurretPos( turret )
        
        ## test if main target is in range
        if game.tick%(config.fps/6)==1 and ship.ai.attacking and ship.ai.attacking.alive and ship.ai.attacking != self.target and self.objectInRange( ship, turret, pos, ship.ai.attacking ): 
            att = self.getAngleToTarget( ship, turret, pos, ship.ai.attacking )
            if self.angleInRange( ship, turret, att ):
                self.target = ship.ai.attacking

        ## already have a target, previous or super
        if self.target and self.objectInRange( ship, turret, pos, self.target ): 
            att = self.getAngleToTarget( ship, turret, pos, self.target )
            if self.angleInRange( ship, turret, att ):
                self.angleToTarget = self.rTarget = att
            else:
                self.target = None

      #  if turret.stats.minAngle != 0 and turret.stats.maxAngle != 0 \
     #     and self.rTarget > turret.stats.maxAngle or self.rTarget < turret.stats.minAngle:
       #     halfUncovered = (2*pi-(turret.stats.maxAngle-turret.stats.minAngle))/2
       #     if self.rTarget > turret.stats.maxAngle:
       #       if self.rTarget < turret.stats.maxAngle+halfUncovered:
       #         self.rTarget = turret.stats.maxAngle
      #        else:
      #          self.rTarget = turret.stats.minAngle
      #      else:
      #        if self.rTarget > turret.stats.minAngle-halfUncovered:
      #          self.rTarget = turret.stats.minAngle
      #        else:
      #          self.rTarget = turret.stats.maxAngle

        ## return to default position
        if not self.target:
            self.angleToTarget = self.rTarget = turret.stats.defaultAngle
        
        ## turn turret
        angleD = angleDiff(self.rTarget, turret.rr)
        if fabs( angleD ) > turret.install.stats.turretSpeed:
            if angleD < 0:
                turret.rr = turret.rr - turret.install.stats.turretSpeed
            else:
                turret.rr = turret.rr + turret.install.stats.turretSpeed
        else:
            turret.rr = self.rTarget

        return ( [], [], [] )

    def getAngleToTarget( self, ship, turret, pos, target ):
        if turret.weapon.stats.speed == 0: 
            targetPos = (target.xp, target.yp)
        else:
            dist = distBetweenObjects( ship, target )
            targetPos = (target.xp+target.xi*dist/turret.weapon.stats.speed, target.yp+target.yi*dist/turret.weapon.stats.speed)
        angle = angleBetween( pos, targetPos )
            
        return (angle-ship.ori)%(2*pi)

    def angleInRange( self, ship, turret, angle ):
         if turret.stats.minAngle == 0 and turret.stats.maxAngle == 0:
             return True
         elif isinstance( turret.weapon, MissileWeaponTurret ):
             return True

         angle = angle % (2*pi)
         if turret.stats.maxAngle < turret.stats.minAngle:
            return not (angle >= turret.stats.maxAngle and angle <= turret.stats.minAngle)
         else:
            return angle <= turret.stats.maxAngle and angle >= turret.stats.minAngle

    def distInRange( self, ship, turret, dist ):
        return dist <= turret.weapon.stats.maxRange and dist >= turret.weapon.stats.minRange

    def objectInRange( self, ship, turret, pos, target ):
        dist = distLowerThanReturn( pos, (target.xp, target.yp), turret.weapon.stats.maxRange+target.stats.maxRadius)
        if dist:
            return dist >= turret.weapon.stats.minRange
        else:
            return False #dist <= turret.weapon.stats.maxRange and dist >= turret.weapon.stats.minRange

class AiWeaponTurret( AiTurret ):
    def doTurn( self, ship, turret, game, attack):

        ## remove dead target
        if self.target and not self.target.alive:
            self.target = None
            
        ## check if target still in range
        if self.target:
            pos = ship.getTurretPos( turret )
            if not self.objectInRange( ship, turret, pos, self.target ):
                self.target = None
            else:
                att = self.getAngleToTarget( ship, turret, pos, self.target )
                if not self.angleInRange(  ship, turret, att ):
                    self.target = None
                    
        ## find new target
        if not self.target and self.foundNothingAt < game.tick: #  and attack: # attack: #-config.fps/2: # doesn't have a target, non or out of range
         #   posTargets = []
            bestObj = None
            bestAngle = 2*pi
            pos = ship.getTurretPos( turret )
            foundSomethingClose = False

          #  bestObj = game.harvestables.getClosestAccording( ship, ship.stats.radarRange, 
	# func=lambda obj: isinstance( obj, Ship ) and obj.alive and obj.player and obj.player != ship.player and game.getRelationBetween( ship.player, obj.player ) < 0 )

            for obj in game.objects.getWithinArea( ship.getTurretPos( turret ), turret.weapon.stats.maxRange ): # TODO check target radius
                if isinstance( obj, Ship ) and obj.alive and obj.player and obj.player != ship.player and obj.ai and obj.ai.attacking and obj.ai.attacking.player and game.getRelationBetween( ship.player, obj.player ) < 0: # and self.objectInRange( ship, turret, pos, obj ): # game.getRelationBetween( obj.ai.attacking.player, ship.player )
                   att = self.getAngleToTarget( ship, turret, pos, obj )
                   foundSomethingClose = True
                   if self.angleInRange(  ship, turret, att ) and fabs( angleDiff( turret.rr, att )) < bestAngle:
                         bestObj = obj

            if bestObj:
                self.target = bestObj
                self.angleToTarget = self.rTarget = bestAngle
            else:
              if foundSomethingClose:
                self.foundNothingAt = game.tick+config.fps/6
              else:
                self.foundNothingAt = game.tick+config.fps/3

        ## return to default position
      #  if not self.target: # still doesn't have a target
      #      self.angleToTarget = self.rTarget = turret.stats.defaultAngle

        ( ao0, ro0, ag0 ) = AiTurret.doTurn( self, ship, turret, game, attack)

        if self.target and turret.weapon.canFire( ship, turret, game ):
            ( ao1, ro1, ag1 ) = self.fireAtWill( ship, turret, game )
            ( ao0, ro0, ag0 ) = ( ao0+ao1, ro0+ro1, ag0+ag1 )

        return ( ao0, ro0, ag0 )

    def fireAtWill( self, ship, turret, game ):
        if isinstance( turret.weapon, LaserWeaponTurret ):
            angleError = pi/8
        else:
            angleError = pi/16
            
        if angleError >= 2*pi or fabs(angleDiff(self.angleToTarget, turret.rr)) < angleError: # * turret.weapon.stats.certainty/100:
            dist = distBetween( ship.getTurretPos( turret ), (self.target.xp, self.target.yp) )
            if dist >= turret.weapon.stats.minRange and dist-self.target.stats.maxRadius <= turret.weapon.stats.maxRange:
                return turret.weapon.fire( ship, turret, game, self.target )
        return ([],[],[])
        
        
class AiWeaponTurretStable( AiWeaponTurret ):
    def fireAtWill( self, ship, turret, game ):
        dist = distBetween( ship.getTurretPos( turret ), (self.target.xp, self.target.yp) )
        if dist >= turret.weapon.stats.minRange and dist-self.target.stats.maxRadius <= turret.weapon.stats.maxRange:
            return turret.weapon.fire( ship, turret, game, self.target )
        else:
            return ([],[],[])
        
class AiSpecialMissileTurret( AiTurret ):
    def doTurn( self, ship, turret, game, attack):
        ( ao0, ro0, ag0 ) = AiTurret.doTurn( self, ship, turret, game, attack)
        if ship.missiles[ turret.weapon.stats.projectile.img ].target \
          and turret.weapon.canFire( ship, turret, game ):
            ( ao1, ro1, ag1 ) = turret.weapon.fire( ship, turret, game, ship.missiles[ turret.weapon.stats.projectile.img ].target )
            ( ao0, ro0, ag0 ) = ( ao0+ao1, ro0+ro1, ag0+ag1 )
            ship.missiles[ turret.weapon.stats.projectile.img ].target = None
        return  ( ao0, ro0, ag0 )

from stats import BuilderMissileStats
class AiBuilderMissileTurret( AiTurret ):
    def doTurn( self, ship, turret, game, attack):
        ( ao0, ro0, ag0 ) = AiTurret.doTurn( self, ship, turret, game, attack)

        for missileId, reserve in ship.missiles.items():
            if isinstance( game.stats[ missileId ], BuilderMissileStats ) and reserve.target:
                for m1 in turret.install.stats.specialValue:
                    if game.stats[ missileId ].buildType == m1:
                        ( ao1, ro1, ag1 ) = turret.weapon.fire( ship, turret, game, ship.missiles[ missileId ].target, missileId=missileId, buildType=m1 )
                        ( ao0, ro0, ag0 ) = ( ao0+ao1, ro0+ro1, ag0+ag1 )
                        ship.missiles[ missileId ].target = None
                        
            
       # for missileId in turret.install.stats.specialValue:
       #     if ship.missiles[ missileId ].target \
       #       and turret.weapon.canFire( ship, turret, game ):
        return  ( ao0, ro0, ag0 )

class AiRotatingTurret( AiTurret ):
    def doTurn( self, ship, turret, game, attack):
        turret.rr = turret.rr+turret.install.stats.turretSpeed
        return ([],[],[])

class AiSolarTurret( AiTurret ):
    def doTurn( self, ship, turret, game, attack):
        if not self.target or game.tick%(config.fps*10)==0:
            sunDist = None
            for obj in game.astres:
                if isinstance( obj, Sun ):
                    dist = distLowerThanObjectsReturn( ship, obj, sunDist )
                    if not sunDist or dist: #dist < sunDist:
                        self.target = obj
                        sunDist = dist

        if self.target:
          angle = angleBetweenObjects( ship, self.target )-ship.ori
          angleD = angleDiff(angle, turret.rr)
          if fabs( angleD ) > turret.install.stats.turretSpeed:
            if angleD < 0:
                turret.rr = turret.rr - turret.install.stats.turretSpeed
            else:
                turret.rr = turret.rr + turret.install.stats.turretSpeed
          else:
            turret.rr = angle

        return ([],[],[])

class AiTargeterTurret( AiTurret ):
    def doTurn( self, ship, turret, game, attack):
        #
        #if not self.target and ship.ai.attacking:
        #    self.target = ship.ai.attacking
        self.target = attack
        if game.tick%(config.fps) == 9:
          if self.target:
            self.rTarget = angleBetweenObjects( ship, self.target )-ship.ori
          else:
            self.rTarget = turret.stats.defaultAngle

        
        angleD = angleDiff(self.rTarget, turret.rr)
        if fabs( angleD ) > turret.install.stats.turretSpeed:
            if angleD < 0:
                turret.rr = turret.rr - turret.install.stats.turretSpeed
            else:
                turret.rr = turret.rr + turret.install.stats.turretSpeed
        else:
            turret.rr = self.rTarget

        return ( [], [], [] )
            

# specialized by transporter, and also harvester and builders throught worker
class AiPilotCivilian( AiPilot ):
    def __init__(self,flagship):
        AiPilot.__init__(self)
        self.flagship = flagship
        self.working = False

    def doTurn( self, ship, game ):
        # idle			
        # harvesting			goTo source
        # idle harvesting		at source
        # orbiting harvesting		atually harvesting
        # idl orbiting harvesting	done harvesting -> docking
	# docking	

        ## abandonned
        if not self.flagship or not self.flagship.alive: #  or not distLowerThanObjects( self.flagship, ship, :
            self.flagship = None
            bestDist = 5000
            
            self.flagship = game.objects.getClosestAccording( ship, 5000, 
	func=lambda obj: isinstance( obj, Ship ) and obj.shipyards and obj.player and ship.stats is obj.player.race.ships )

            if self.flagship: 
                self.flagship.shipyards[ ship.stats.img ].away.append( ship )
                ship.player = self.flagship.player
            else:
                ship.die( game )

        ## if still idle
        if not self.dockingTo and self.flagship and not self.working: # found nothing
        
            for turret in ship.turrets:
                if turret.ai:
                    turret.ai.target = None
                
            self.goTo( ship, self.getRandomGuardPosition(ship, self.flagship, 2) )

        return AiPilot.doTurn( self, ship, game )

    def dock( self, ship, target, game ):
        self.goingTo = None
        AiPilot.dock( self, ship, target, game )

    def died( self, ship, game ):
        if self.flagship:
            self.flagship.removeShip( ship )

    def getSearchRange( self, ship ):
        return ship.stats.maxRange

class AiPilotWorker( AiPilotCivilian ):
    def __init__(self,flagship):
        AiPilotCivilian.__init__(self, flagship)
        self.working = False

    def doTurn( self, ship, game ):

        if self.working:
            for turret in ship.turrets:
                if turret.ai:
                    turret.ai.target = self.working

            if self.workIsDone( ship ):
                self.idle = True
                self.working = False
                for turret in ship.turrets:
                    if turret.ai:
                        turret.ai.target = None

                self.dockingTo = self.flagship
                self.orbiting = False
            elif not ship.orbiting: # self.idle and 
                self.goTo( ship, self.working, orbitAltitude=0.8 )

        # turrets / weapons
        for turret in ship.turrets:
            if turret.ai:
                turret.ai.doTurn( ship, turret, game, self.working)
        return AiPilotCivilian.doTurn( self, ship, game )

    def workIsDone( self, ship ):
        return False

    def dock( self, ship, target, game ):
        self.working = False
        AiPilotCivilian.dock( self, ship, target, game )


#from ships import FlagShip
class AiPilotHarvester( AiPilotWorker ):
    def __init__(self,flagship):
        AiPilotWorker.__init__(self,flagship)

    def workIsDone( self, ship ):
        return ship.ore >= ship.stats.maxOre

    def doTurn( self, ship, game ):

        ## if idle and worth looking for ore
        if not self.dockingTo and not self.working and self.flagship and self.flagship.noOreCloseAt < game.tick-3*config.fps:
            ## try to find more ore
            distFound = ship.stats.maxRange+1
            
            self.working = self.getClosestAsteroid( ship, game )
            
            if not self.working:
                self.flagship.noOreCloseAt = game.tick

        return AiPilotWorker.doTurn( self, ship, game )

class AiPilotBuilder( AiPilotWorker ):
    def __init__(self,flagship):
        AiPilotWorker.__init__(self,flagship)

    def workIsDone( self, ship ):
        return ship.ore < 1 \
         or (self.working and not self.working.alive)

    def doTurn( self, ship, game ):
        from ships import Scaffolding
        
        if not self.dockingTo and not self.working:
            self.working = self.getClosestScaffolding( ship, game )

        return AiPilotWorker.doTurn( self, ship, game )

class AiPilotTransporter( AiPilotCivilian ):
    def __init__(self,flagship):
        AiPilotCivilian.__init__(self,flagship)

    def doTurn( self, ship, game ):
        if game.tick % 21 == 0:

           # self.idle = not self.working
            if not self.dockingTo: # and self.idle: # not self.dockingTo: # dockingTo: self.working or
                
                if ship.ore < 1:
                    self.dockingTo = self.flagship
                    self.working = False
            #        print "go back to flagship"
                else:
                    # find other flagship in need
                    foundInNeed = self.getNeediestShip( ship, game )
                    self.working = foundInNeed
                    self.dockingTo = foundInNeed
                    self.idle = True
                   # if foundInNeed:
                        #self.goTo( ship, inNeedOfOre )
                   #     print "transport to ", foundInNeed
                    #else:
                        #self.dockingTo = self.flagship
                       # self.working = False
            #            print "nothing found"
            #else:
            #    print "a"
                            
            #self.idle = not self.working
            #print self, self.idle, self.working, self.dockingTo

        return AiPilotCivilian.doTurn( self, ship, game )
            
    def caresAboutShipNeeds( self, ship, otherShip ):
        print "cares? ",  otherShip != self.flagship 
    	return otherShip != self.flagship 


# from ais import AiCaptain
#from ships import FlagShip
class AiCivilian( AiPilot ):
    def __init__( self ):
        AiPilot.__init__( self )
        self.follows = None
        self.lastPosAt = 0
        self.patience = config.fps * 2

    def doTurn( self, ship, game ):
        if self.follows and not self.follows.alive:
            self.follows.civilianShips.remove( ship )
            self.follows = None

        if not self.follows and game.tick%20 == 0:

            fs = game.objects.getClosestAccording( ship, ship.stats.influenceRadius, 
	func=lambda obj: isinstance( obj, Ship ) and obj.shipyards )

            if fs:
                self.follows = fs
                self.follows.civilianShips.append( ship )
        
        if self.follows:
            if game.tick%120 == 0:
              valueFollowed = self.evalShip( self.follows )
              for obj in game.objects.getWithin( ship, ship.stats.influenceRadius ): #objects:
                if isinstance( obj, Ship ) and obj.shipyards and distLowerThanObjects( ship, obj, ship.stats.influenceRadius ):
                    valueOther = self.evalShip( obj )
                    if float(valueOther)/valueFollowed > float(len( obj.civilianShips )+1) / (len( self.follows.civilianShips)+1):
                       self.follows.civilianShips.remove( ship )
                       self.follows = obj
                       self.follows.civilianShips.append( ship )
                
            if self.idle or self.lastPosAt < game.tick - self.patience:
                # get random position
                self.goTo( ship, self.getRandomGuardPosition( ship, self.follows, 2 )  )
                self.lastPosAt = game.tick

        elif not self.goingTo and not ship.orbiting: # found nothing to follow
            oo = None
            ooDist = ship.stats.influenceRadius*10
            for obj in game.astres:
                if obj.stats.orbitable:
                    dist = distLowerThanObjectsReturn( ship, obj, ooDist )
                    if dist: # distLowerThanObjects( ship, obj ): #dist < ooDist:
                        oo = obj
                        ooDist = dist
            if oo: 
                self.goTo( ship, oo )

        ( ao, ro, ag ) = AiPilot.doTurn( self, ship, game )
        return ( ao, ro, ag )

    def evalShip( self, ship ): # TODO
        return ship.civilianValue

    def died( self, ship, game ):
        if self.follows:
            self.follows.civilianShips.remove( ship )

class AiPlayer:
    def __init__( self, player ):
        self.player = player

    def doTurn( self, game ):
        pass

# class Player
# class Captain FlagShip Governor
# class fighter
# class harvester
# class ? harvesterDispatcher
# class civilian ship

# AITurretDummy
# AiTurretRotating
# AiTurretCombat



