
#
# This file contains ids of images (mostly) shared between server and client.
#
# TODO Assign id numbers in an auto-incremental way, has been put off in order to simplify debugging. Could be using alphanumeric ids and save bandwidth
#

chars = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
idPos = 0
def getId():
    id = ""
    
    idPos += 1
    return id


### asteroids ids
# there mainly for consistency
A_0		= 0
A_1		= 1
A_2		= 2
A_3		= 3
A_4		= 4


### Ships
# human's
S_FLAGSHIP_0 	= 10
S_FLAGSHIP_1 	= 11
S_FLAGSHIP_2 	= 12
S_FIGHTER 	= 13
S_BOMBER 	= 14

S_HARVESTER 	= 15

S_CIVILIAN_0	= 16

S_ORBITALBASE 	= 17

S_MINE	 	= 18

# ai's
S_AI_BASE 	= 20
S_AI_FIGHTER 	= 21
S_AI_FS_0 	= 22
S_AI_FS_1 	= 23
S_AI_FS_2 	= 24
S_AI_BOMBER 	= 25
S_AI_HARVESTER 	= 26

# nomad's
S_NOMAD_FS_0 	= 30
S_NOMAD_FS_1 	= 31
S_NOMAD_FS_2 	= 32
S_NOMAD_BASE	= 33
S_NOMAD_FIGHTER	= 34
S_NOMAD_HARVESTER	= 35
S_NOMAD_HARVESTER_1	= 36

# evolved's
S_EVOLVED_FS_0 	= 40
S_EVOLVED_FS_1 	= 41
S_EVOLVED_FS_2 	= 42
S_EVOLVED_FIGHTER = 43
S_EVOLVED_BOMBER = 44
S_EVOLVED_HARVESTER 	= 45

# extras's
S_EXTRA_FS_0 	= 50
S_EXTRA_FS_1 	= 51
S_EXTRA_FS_2 	= 52
S_EXTRA_FIGHTER = 53
S_EXTRA_BOMBER 	= 54
S_EXTRA_HARVESTER 	= 55

### Weapons
# human's
W_LASER_SR 	= 100
W_LASER_MR_0 	= 101
W_LASER_MR_1 	= 102

W_MASS_SR 	= 111
W_MASS_MR 	= 110
W_MASS_LR 	= 112

W_MISSILE 	= 120
W_NUKE	 	= 121
W_PULSE 	= 122
W_MINER 	= 123
W_PROBE 	= 124
W_COUNTER	= 125

W_BOMB_0 	= 131

W_HARVESTER_T 	= 140

# ai's
W_AI_MISSILE	= 150

# extra's
W_ROCK_THROWER_0	= 160
W_ROCK_THROWER_1	= 163
W_DRAGON_0		= 161
W_LARVA_0		= 162
W_EXTRA_FIGHTER		= 164
W_EXTRA_BOMBER		= 165


### bullets / projectiles
# MISSILE_0	= 200
B_BULLET_0	= 201
B_BOMB_0	= 202
B_ROCK_0	= 203
B_ROCK_1	= 204
B_AI_0		= 205
B_FIRE_0	= 206
B_EGG_0		= 207

### Turrets
# human's Ts (and basics)
T_LASER_SR 	= 300
T_LASER_MR_0 	= 301
T_LASER_MR_1 	= 302

T_MASS_MR 	= 310
T_MASS_SR_0 	= 311
T_MASS_SR_1 	= 313
T_MASS_SR_2 	= 314
T_MASS_LR 	= 312
T_MASS_MR_1     = 315

T_MISSILES_0 	= 320
T_MISSILES_1 	= 321
T_MISSILES_2 	= 323

T_HARVESTER 	= 330
T_SPOTLIGHT 	= 331
T_RED_SPOTLIGHT = 332

T_INTERDICTOR 	= 341
T_NUKE	 	= 342
T_PULSE 	= 343
T_RADAR 	= 344
T_BUILDING 	= 345
T_GENERATOR 	= 346
T_SOLAR_0 	= 347
T_HANGAR 	= 348
T_REPAIR 	= 349
T_SHIELD_RECHARGE 	= 350
T_MAXSHIELD 	= 351
T_MINER 	= 352
T_COUNTER 	= 353
T_BIOSPHERE	= 354
T_SOLAR_1 	= 355
T_SOLAR_2 	= 356
T_SUCKER 	= 357
T_EJUMP 	= 358
T_INERTIA 	= 359
T_BIOSPHERE_1	= 360
T_SAIL		= 361
T_JAMMER	= 362
T_SCANNER	= 363

# ai's Ts
T_AI_MISSILE_0	= 370

# extra's Ts
T_ROCK_THROWER_0	= 380
T_ROCK_THROWER_1	= 383
T_DRAGON_0		= 381
T_LARVA_0		= 382

### Turret AI type
# ?why isn't it the class passed directly as argument of the stats? ...there must be a reason...
TA_COMBAT_STABLE 	= 400
TA_COMBAT_ROTATING 	= 401
TA_ROTATING 		= 402
TA_SOLAR 		= 403
TA_HARVESTER 		= 404
TA_MISSILE_SPECIAL 	= 405
TA_TARGET		= 406

### Weapon Type
## Allows build of the correct inheritance of Weapon
WT_LASER		= 410
WT_MASS			= 411
WT_BOMB			= 412
WT_MISSILE		= 413
WT_MISSILE_SPECIAL 	= 414

### Orders
O_MOVE			= 500
O_STOP_MOVE		= 501
O_ATTACK		= 502
O_ORBIT			= 503
O_BUILD_TURRET		= 504
O_BUILD_SHIP		= 505
O_BUILD_MISSILE		= 506
O_LAUNCH_MISSILE	= 507
O_CHARGE		= 508
O_REPAIR		= 509

O_RECALL_SHIPS 	= 510
O_LAUNCH_SHIPS 	= 511

O_JUMP_NOW 	= 520
O_JUMP		= 521

O_TURRET_ACTIVATE	= 522
O_RELATION		= 523
O_SELF_DESTRUCT		= 524


### Relations type with objects sent on the network
U_FLAGSHIP 	= 600
#U_FLAGSHIP_TURRET	= 601
U_OWN		= 602
U_FRIENDLY	= 603
U_ENNEMY	= 604
U_RESOURCE	= 605
U_ORBITABLE	= 606
U_NEUTRAL	= 607

### Astres type
A_SUN		= 200
A_PLANET	= 210
A_NEBULA	= 220
A_BLACK_HOLE	= 230


### Planets
S_SOL		= 700
P_MERCURY	= 701
P_VENUS		= 702
P_EARTH		= 703
P_MARS		= 704
P_JUPITER	= 705
P_SATURN	= 706
P_NEPTUNE	= 707

P_MOON		= 710
P_X		= 711
P_MARS_1	= 712
P_MARS_2	= 713
P_JUPITER_1	= 714
P_MERCURY_1	= 715
P_X_1		= 716
P_SATURN_1	= 717

P_ALPHA_1	= 720
P_ALPHA_2	= 721

P_BETA_1	= 730
P_BETA_2	= 731

P_GAIA		= 740

### Gfxs
# TODO: should be changed to Fxs. ?worth it?
G_LASER_SMALL	= 800
G_EXPLOSION	= 801
G_SHIELD	= 802
G_FRAGMENT	= 803
G_EXHAUST	= 804

R_NEUTRAL	= 1000
R_HOSTILE	= 1001
R_ALLIED	= 1002

F_LARGE_0	= 2000
F_LARGE_1	= 2001

F_FLAGSHIP_0	= 2002
F_FLAGSHIP_1	= 2003
F_FLAGSHIP_2	= 2004

F_FIGHTER_0	= 2005
F_FIGHTER_1	= 2006
F_FIGHTER_2	= 2007

F_AI_0		= 2008

### Exhauts / trails
# temporary deactivated/uselesss
E_0		= 2100
E_1		= 2101
E_2		= 2102

### Missiles
M_NORMAL	= 2200
M_NUKE		= 2201
M_PULSE		= 2202
M_MINER		= 2203
M_PROBE		= 2204
M_COUNTER	= 2205
M_AI		= 2206
M_LARVA		= 2207

### Special ability of turrets
S_INTERDICTOR	= 3000
S_NUKE		= 3001
S_PULSE		= 3002
S_MINE		= 3003
S_RADAR		= 3004
S_REACTOR	= 3005
S_SOLAR		= 3006
S_HANGAR	= 3007
S_MINER		= 3008
S_CIVILIAN	= 3009
S_COUNTER	= 3010
S_SUCKER	= 3011
S_INERTIA	= 3012
S_SAIL		= 3013
S_JAMMER	= 3014
S_SCANNER	= 3015
# S_TRACTOR_AGR   = 3016

### Sound fxs
## Explosions
S_EX_FIRE	= 3100
S_EX_JUMP	= 3101
S_EX_SHIP	= 3102
S_EX_NUKE	= 3103
S_EX_PULSE	= 3104

### Categories of turret
# TODO: to be removed?
C_WEAPON	= 3200
C_MISSILE	= 3201
C_OTHER		= 3202

### Races
R_HUMAN		= 3300
R_AI		= 3301
R_NOMAD		= 3302
R_EXTRA		= 3303
R_EVOLVED	= 3304

