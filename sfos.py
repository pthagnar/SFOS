#!/usr/bin/python3

from random import uniform, choice, sample, gauss
import os, sys
from time import strftime

def weighted_choice(choices):
	total = sum(w for c, w in choices)
	r = uniform(0, total)
	upto = 0
	for c, w in choices:
		if upto + w > r:
			return c
		upto += w
	assert False, "Shouldn't get here"

#grouped by magnitude
starglyphs = [
              ["✸","✱"],
              ["✷","✶"],
              ["*","+"],
              ["✦","★"],
              ["˚","⋆"],
              [".","·","˙"],
              ["·","˙"],
             ]

def get_stars(n):
    
    stars = []
             
    #http://www.stargazing.net/david/constel/howmanystars.html
    proportions = [8,14,71,190,610,1929,5946]
    
    for i in range(n):
        s = weighted_choice(list(zip(range(7),proportions)))
        stars += [choice(starglyphs[s])]   
    return stars


#when run on startup, this defaults to dumping files in ~ -- make it not do that
#by finding the script path and changing the working directory to that
scriptpath = os.path.dirname(os.path.realpath(sys.argv[0]))
os.chdir(scriptpath)

#get monitor info
#TURNS OUT: if u run xrandr too much, this fucks up x : a temp file it IS

#if it's already present, just read from that
if os.path.isfile("resolution_info"):
    resfile = open("resolution_info","r")
    resline = resfile.readlines()[0].strip()
    resfile.close()
    width, height = [int(n) for n in resline.split(" ")]

else:
    #get screen info
    screen = os.popen("xrandr -q -d :0").readlines()[0]
    width, height = int(screen.split()[7]), int(screen.split()[9][:-1])

    #write it
    resfile = open("resolution_info","w")
    resfile.write("{} {}".format(width,height))
    resfile.close()

#the size of text blocks
glyphwidth, glyphheight = 7, 14
#TODO: include some way to calculate this based on the size of the font

#this is how long the strings should be + how many of them there should be
fieldwidth, fieldheight = int(width/glyphwidth), int(height/glyphheight)

def get_field():
    '''Generates an empty list of lists of " " of the right size for pop'ing'''
    return [[" " for i in range(fieldwidth)] for j in range(fieldheight)]

#get all the valid coordinates of fields
coords = []
for x in range(fieldwidth):
    for y in range(fieldheight):
        coords += [(x,y)]

#STARS
#==============

stardensity = choice(range(1,15))
numstars = int(stardensity/100 * (fieldwidth * fieldheight))

#get a list of the star glyphs we will use
stars = get_stars(numstars)

#get the coordinates where there will be stars
locs = sample(coords,numstars)

#makes empty fields for the colours of stars we will have
redfield = get_field()
yellowfield = get_field()
whitefield = get_field()
bluefield = get_field()

#FIXME tidy
#make sublists of the coordinates with stars of the colours we will have
redlocs = locs[:int(len(locs)/4)]
yellowlocs =locs[int(len(locs)/4):int(len(locs)/2)]
whitelocs = locs[int(len(locs)/2):-1*int(len(locs)/8)]
bluelocs = locs[-1*int(len(locs)/8):]

#collect together our fields and coordinate lists
fields = [redfield,yellowfield,whitefield,bluefield]
all_locs = [redlocs,yellowlocs,whitelocs,bluelocs]

#BRITESTARS
#==========

#britestars get shine and are possible nebula sources
#maybe they will get constellations too
#maybe names!

#coords and field
britelocs = []
britefield = get_field()

#stars of magnitudes 0-2 are britestars
briteglyphs = "".join(starglyphs[0] + starglyphs[1] + starglyphs[2])


#BACK TO STARS
#=============

#go over all the colours of stars, fields + locs
for this_field, this_type in zip(fields,all_locs):
    for coord in this_type:
        #pop a star from the list
        this_star = stars.pop()
        #add to field
        this_field[coord[1]][coord[0]] = this_star
        #work out if it is a britestar
        shine_brite = False
        if this_star in briteglyphs:
            shine_brite = True
        #and if so, add a twinkle to the britefield + mark a location
        if shine_brite:
            britefield[coord[1]][coord[0]] = "⋆"
            britelocs += [(coord[1],coord[0])]
    
#GALAXY
#======

#only include one 50% of the time
has_galaxy = False
galaxy_prob = 0.50
if uniform(0,1) < galaxy_prob:
    has_galaxy = True

#the galaxy is the first thing printed [b/c most distant!], so there has to be 
#a galaxyfield, even if it is blank
if not has_galaxy:
    galaxyfield = get_field()
        
else:
    #the sd of the spread is +-3 glyphs
    thickness = 3
    #we generate five straight lines and spread each out gaussianly
    density = 5

    def get_galaxy_datum(x,leftside,rightside,width):
        '''
        The galaxy starts off as a straight line, from which fluff() blurs it.
        This gets the datum to begin with and results in a linear galaxy
        TODO: make it curve!
        '''
        if leftside < rightside:
            sign = +1
        else:
            sign = -1
        step = abs(leftside - rightside)/width
        return leftside + sign*(x*step)

    def fluff(n):
        '''spread about by thickness'''
        return int(n + int(gauss(0,thickness)))

    #coords and field        
    galaxyfield = get_field()
    galaxy_coords = []
    
    #the left and right anchors of the datum of the galaxy can be anywhere visible
    leftside = choice(range(fieldheight))
    rightside = choice(range(fieldheight))

    #populate the coordinate list with galaxy cloud coordinates, taking the datum
    #and fluffing them in BOTH dimensions
    for i in range(fieldwidth):
        this_coord = get_galaxy_datum(i,leftside,rightside,fieldwidth)
        galaxy_coords += [(fluff(i), fluff(this_coord) ) for d in range(density)]

    #filter the coordinate list for duplicates
    galaxy_coords = list(set(galaxy_coords))

    #populate the galaxy field with cloudy glyphs
    for coord in galaxy_coords:
        try:
            galaxyfield[coord[1]][coord[0]] = choice("░▒")
        #don't bother if it's offscreen
        except IndexError:
            pass
        
#NEBULAE
#======
#one nebula at the moment

#10% chance of nebula
has_nebula = False
nebula_prob = 0.1
if uniform(0,1) < nebula_prob:
    has_nebula = True
    
#if for some reason there are no britestars [eg low star density], there can
#be no nebulae

if not britelocs:
    has_nebula = False
    
if has_nebula:
    #pick a random britestar to illuminate the nebula
    #FIXME it should prefer stars not too near the edge
    nebulaloc = choice(britelocs)

    #these are the same colours as are used by stars
    neb_colour = choice(("red","green","yellow","blue","magenta","cyan","grey"))

    #sd is +- nebulathick glyphs
    nebulathick = choice(range(2,10))
    
    #how many cloud glyphs there are -- roughly the cube of the size
    #.'. constant density of gas-cloud
    nebulapuff = (2 * nebulathick) **3

    #TODO make this better -- glyphs not square, make blobs more circular
    #this makes the nebulae different aspect ratios [also densities, since
    #independent of nebulapuff]
    nebheight, nebwidth = uniform(0,2), uniform(0,1)
    
    #like fluff, but broader-minded
    def puff(n,t):
        return int(n + int(gauss(0,t)))

    #coords and field
    nebulafield = get_field()    
    nebulalocs = []

    #similar to galaxy here
    for i in range(nebulapuff):
        nebulalocs += [(puff(nebulaloc[0],nebulathick*nebwidth),puff(nebulaloc[1],nebulathick*nebheight))]
    
    #filter duplicates
    nebulalocs = list(set(nebulalocs))

    #populate nebula field
    for coord in nebulalocs:
        try:
            nebulafield[coord[0]][coord[1]] = choice("░▒")
        #don't bother if it's offscreen
        except IndexError:
            pass
      
#PLANETS
#TODO
#======

#symbol, semi-major axis / 10**6 km, inclination to ecliptic deg, colour

planets = {
          "sun":("⊙",0,0,"yellow"),
          "mercury":("☿",58,7.0, "white"),
          "venus":("♀",108,3.3, "white"),
          "mars":("♂",228,1.89, "red"),
          "jupiter":("♃",779,1.31, "yellow"),
          "saturn":("♄",1433,2.49, "yellow"),
         }

#twice the orbit of saturn in display characters
solar_system_length = 250
solar_system_height = 2

has_planets = False
#the plane of the ecliptic and the galactic plane are ~60 degrees apart
#write that down

#first item:
#0 here is the leftmost part, progressing through to a max at solar_system_length
#second item:
#the offset from the ecliptic

planetlocs = {}
#farthest + incliningest planets are scale
len_scale = solar_system_length / planets["saturn"][1]
hei_scale = solar_system_height / planets["venus"][2]

for planet in planets:
    sma, incl = len_scale*planets[planet][1], hei_scale*planets[planet][2]
    planetlocs[planet] = (int(solar_system_length/2 + uniform(-sma,sma)),
                          int(uniform(-incl,incl)))

print(planetlocs)

#place the sun
sun_coords = (0,0)

#get ecliptic

#calculate planet coords

#populate planetfield

#MOON
#TODO
#=====

#HORIZON
#=======
#The horizon is a random walk up and down
#There are two levels of horizon:
#* full glyphs which go up and down in a true random walk -- looks very craggy + built up
#* smaller glyphs which use fractional blocks and just loop over a glyphlist
#  i.e. after reaching the max size, going up means getting smaller and v.v.

#only print horizon 50% of time
has_horizon = False
horizon_prob = 0.5
if uniform(0,1) < horizon_prob:
    has_horizon = True
    
#here are the smaller glyphs in order; doesn't that look weird?
horizon_glyphs = "▁▂▃▄▅▆▇█▇▆▅▄▃▂"
    
if has_horizon:

    #no coords, just field
    horizonfield = get_field()
        
    #horizon starts off somewhere between 10% and 25% from the bottom
    horizonheight = fieldheight - int(fieldheight * uniform(0.1,0.25))
    #and starts off at the halfway high block [this is the index of horizon_glyphs]
    little_height = 3

    #transition probs for full glyphs
    up_prob = 0.05
    down_prob = 0.05
    #transition probs for little glyphs
    l_up_prob = 0.1
    l_down_prob = 0.1
    #the blocks are 1/8 of a box -- make it rougher by skipping blocks
    l_trans_amount = 1
    
    for i in range(fieldwidth):
        #go up, go down, w/e
        if uniform(0,1) < up_prob:
            horizonheight += 1
        if uniform(0,1) < down_prob:
            horizonheight += -1
        #wrap around when you reach the end
        if uniform(0,1) < l_up_prob:
            little_height = (little_height + l_trans_amount) % len(horizon_glyphs)
        if uniform(0,1) < l_down_prob:
            little_height = (little_height - l_trans_amount) % len(horizon_glyphs)
         
        for j in range(fieldheight - horizonheight):
                #7 is the full box
                #print the horizon with this
                horizonfield[-j - 1][i] = horizon_glyphs[7]
                #except the topmost has the appropriate little glyph
                horizonfield[horizonheight][i] = horizon_glyphs[little_height]
        
#CONSTELLATIONS
#TODO
#======
has_constellations = False

#NAMES
#=====
#uses Leonard Richardson's olipy library to generate star names
#actually uses 'Queneau assembly' - popularised for this purpose by ibid. - not Markov chains
#the corpus is a mixture of real + fictional stars

#names are displayed 50% of the time
has_names = False
names_prob = 0.5
if uniform(0,1) < names_prob:
    has_names = True

if has_names:
    from queneau import WordAssembler

    stars = ["Sirius","Aldebaran","Algol","Canopus","Albemuth","Betelgeuse","Mirach",
             "Almach","Altair","Thalimain","Hamal","Capella","Arcturus", "Mirak",
             "Mirzam", "Procyon", "Deneb", "Rigel", "Menkar", "Mira", "Gemma",
             "Mimosa", "Deneb", "Arrakis", "Castor", "Pollux", "Propus", "Regulus",
             "Nihal", "Vega", "Bellatrix", "Fomalhaut", "Ascella", "Arkab", "Antares",
             "Alcyone", "Atlas", "Electra", "Maia", "Merope", "Pleione", "Celaeno",
             "Asterope", "Merak", "Megrez", "Alioth", "Mizar", "Alcor", "Talitha",
             "Tania", "Alula", "Muscida", "Polaris", "Kochab", "Stella", "Astra",
             "Sidera", "Suhail", "Markab", "Spica", "Maria", "Eridanus",
             "Caladan", "Cassiopeia", "Cynosure", "Phecda", "Alphard", "Acamar",
             "Achernar", "Adhara", "Adhafera", "Aladfar", "Albadah", "Alderamin",
             "Algiedi", "Algenib", "Alkes", "Alpheratz", "Wallach", "Corrino",
             "Ascella", "Asterion", "Azelfafage", "Nigelfarage", "Baham", "Caph", "Chara",
             "Cheleb", "Kolob", "Electra", "Grumium", "Haedus", "Hoedus", "Jabbah",
             "Kabdhilinan", "Kastra", "Kochab", "Kitalpha", "Lesath", "Lucida",
             "Elbereth", "Media", "Merak", "Miram", "Mothallah", "Nihal", "Phact",
             "Propus", "Suhail", "Ruchba", "Sadalbari", "Sabik", "Sadalmelik",
             "Sadalsuud", "Sadatoni", "Sadr", "Saiph", "Salm", "Tarazed"]

    star_corpus = WordAssembler(stars)

    britestar_names = [star_corpus.assemble_word() for britestar in britelocs]

#EASTER EGGS
#TODO
#======
#comet
#-----
#very rare -- maybe 1/10000

#christmas
#---------
#horizon is white december -- january
#father christmas on christmas eve

#12 days of christmas, angels 👼, bright star

#star of david/✡
#---------------
#jew holidays?

#ufo/👽👾
#-------
#same rarity as comet

#=================
#SETUP COMPLETE
#=================
#ON TO GENERATION
#=================

#our colours
colours = ["red","yellow","green","cyan","blue","magenta","white","black","grey"]

#we have various modes i.e. colour schemes
#each has a probability of being selected -- arbitrary weights later summed up
#and each colour in the colours list above has a corresponding imagemagick
#colour associated with it

colour_modes = {
                "ansi" : (100,("red",
                               "yellow",
                               "green2",
                               "cyan",
                               "blue",
                               "magenta",
                               "white",
                               "black",
                               "grey25")
                         ),
                "pale" : (200,("salmon1",
                               "khaki",
                               "\"#001000\"",
                               "LightSteelBlue2",
                               "blue",
                               "magenta",
                               "white",
                               "black",
                               "grey15")
                         ),
                "red"  : (10 ,("red",
                               "red",
                               "maroon",
                               "red",
                               "maroon",
                               "red",
                               "red",
                               "black",
                               "maroon")
                         ),
                "starmap": (10,("black",
                                "black",
                                "grey75",
                                "black",
                                "grey33",
                                "grey33",
                                "black",
                                "white",
                                "grey25")
                           ),
               }

#wrap all the colours up
colour_dict = {}
for mode in colour_modes:
    actual_colours = colour_modes[mode][1]
    act_dic = {colours[i] : actual_colours[i] for i in range(len(colours))}
    colour_dict[mode] = act_dic

#pick a colour
COLOUR_MODE = weighted_choice([(name, colour_modes[name][0]) for name in colour_modes])

#make things more concise by defining this
get_col = colour_dict[COLOUR_MODE]

#get the date so the filename is timestamped
#this allows for a historical record of backgrounds generated

#TODO: think about increasing granuarity?
datestr = strftime("%Y%m%d")
filename = datestr + "stars.png"

#the temp file is because the graphics are done by calling imagemagick a lot
#when this works properly, the fade-in of the new features arriving is an attractive
#starting-up look, but i think it breaks gnome, so /tant pis/
t_filename = "temp" + filename

def draw_field(field,colour):
    '''
    Turns a field into a long string suitable for imagemagick's convert
    Actually runs convert for each field
    TODO: link all this up into one long imagemagick string and run at end
    '''
    printstr = ""
    for line in field:
        printstr += "".join(line) + "\n"
        
    sysstr = "convert {1} -pointsize 14 -font DejaVu-Sans-Mono-Book -fill {0} -interline-spacing -3 -draw".format(colour,t_filename)
    os.system(sysstr + " \"text 0,0 \' {0} \'\" {1}  ".format(printstr,t_filename))

#convert the galaxy field into a long string suitable for imagemagick
#for the other glyphs this is done in the appropriate imagemagick function
#but the galaxy is special, b/c first
galaxystr = ""
for line in galaxyfield:
    galaxystr += "".join(line) + "\n"
    
#draw black + maybe galaxy
sysstr = "convert -size {0}x{1} ".format(width,height) + "xc:{} -pointsize 14 -font DejaVu-Sans-Mono-Book -fill {} -interline-spacing -3 -draw".format(get_col["black"], get_col["grey"])
os.system(sysstr + " \"text 0,0 \' {0} \'\" {1}  ".format(galaxystr,t_filename))

#draw nebula
if has_nebula:
    draw_field(nebulafield,get_col[neb_colour])
    
#draw stars
draw_field(bluefield,get_col["cyan"])
draw_field(whitefield,get_col["white"])
draw_field(yellowfield,get_col["yellow"])
draw_field(redfield,get_col["red"])

#draw briteness
draw_field(britefield,get_col["white"])

#draw names
if has_names:
    for name, loc in zip(britestar_names,britelocs):
        print(name)
        x, y = loc[1]*(glyphwidth+1) + 5, loc[0]*glyphheight - 5
        sysstr = "convert {1} -pointsize 9 -font DejaVu-Sans-Mono-Book -fill {0} -interline-spacing -3 -draw".format(get_col["white"],t_filename)
        os.system(sysstr + " \"text {2},{3} \' {0} \'\" {1}  ".format(name,t_filename,x,y))

#draw horizon
if has_horizon:
    draw_field(horizonfield,get_col["green"])
    
#rename temp file to proper file
os.system("mv %s %s" % (t_filename,filename))
    
#set background
os.system("gsettings set org.gnome.desktop.background picture-uri file://" + scriptpath + "/" + filename)

#DONE
#====

#TODO some way of archiving and tidying up historical generated images
#FIXME find out why this sometimes upsets gnome + makes it stop updating background +
#     makes opening images in gnome files stop working
