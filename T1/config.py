SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
FPS = 60

COLOR_BG = (20, 15, 30)
COLOR_MOON = (240, 240, 220)
COLOR_GRASS = (34, 110, 50) #copy pasted the colour code from google cuz obiviously i cant memorize this
COLOR_TEXT = (240, 240, 240)
COLOR_ROCKET_BODY = (255, 0, 63) #i thought neon red seems poping out idk 
COLOR_ROCKET_NOSE = (31, 81, 255)   #blue goes with red its universal 
COLOR_PUMPKIN = (255, 95, 31) # the prime enemy projectile
COLOR_SLIDER_BG = (60, 50, 80)
COLOR_SLIDER_HANDLE = (200, 160, 50)

GRAVITY = 9.80665 # I wanted to see what happens when g is to 5d.p
AIR_DENSITY = 1.225 #this is at sea level, im adding a dynamic air density stuff as welll. the formulaas are so annoying 

ROCKET_WIDTH = 24 #last week nightmares
ROCKET_HEIGHT = 90
ROCKET_DRY_MASS = 1.2 #seems like a ok weight for a payload and structure
FUEL_INITIAL = 1.5
FUEL_BURN_RATE = 0.25
THRUST_MAX = 4.0 #after this it has to be a spaceshot or a HPR
MAX_TVC_ANGLE = 15.0

CD_ROCKET = 0.4
CD_PARACHUTE = 1.8

# Default PID Gains for TVC Stabilization   
KP_DEFAULT = 2.2#ai helped bits idk bout PID too complex for me
KI_DEFAULT = 0.05
KD_DEFAULT = 1.4

MAX_HEALTH = 15 #now this is the game part



