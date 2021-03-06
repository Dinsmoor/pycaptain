from campaigns import Campaign

from tutorial1 import Tutorial1
from tutorial2 import Tutorial2
from tutorial3 import Tutorial3

class Tutorial( Campaign ):
    # strings displayed on screen
    title = _("Tutorial")
    player = _("Recruit")
    race = _("Human")
    description = _("Learn fundamentals of PyCaptain through a few missions")
    
    name = "tutorial" # must be the same as containing folder and class title will be .name.capitalize()
    uid = name + "0" # must be unique through versions, will validate saved games against
    
    # import scenario above and list them here
    scenarios = [ Tutorial1,
                  Tutorial2,
                  Tutorial3 ]
    
