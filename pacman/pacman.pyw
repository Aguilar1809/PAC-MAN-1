# REALIZADO POR: JUAN, JOSE, DARIO, SULMY Y YULY
# ESTUDIANTES DEL PROGRAMA DE ESTUDIOS DE COMPUTACION E INFORMATICA
# INSTITUTO DE EDUCACION SUPERIOR TECNOLOGICO PUBLICO - ACORA
# Realizado para el curso de TALLER DE PROGRAMACION CONCURRENTE:

#IMPORTANCION DE LIBRERIAS
import pygame, sys, os, random
from pygame.locals import *

# OBTENCION DE LA RUTA SCRIPT - PYTHON
SCRIPT_PATH=sys.path[0]

#CONFIGURACION DE CONSTANTES Y VARIABLES
NO_GIF_TILES=[23]

NO_WX=0 #
USER_NAME="Pepit@s" 

# Joystick 
JS_DEVNUM=0 
JS_XAXIS=0 
JS_YAXIS=1 
JS_STARTBUTTON=0 

# CONFIGURACION SONIDO Y JOYSTICK
pygame.mixer.pre_init(22050,16,2,512)
JS_STARTBUTTON=0
pygame.mixer.init()

clock = pygame.time.Clock()
pygame.init()

# CONFIGURACION DE LA VENTANA DEL JUEGO
window = pygame.display.set_mode((1, 1))
pygame.display.set_caption("Pacman")

screen = pygame.display.get_surface()

#CARGA DE SONIDOS E IMAGENES
img_Background = pygame.image.load(os.path.join(SCRIPT_PATH,"res","backgrounds","1.gif")).convert()

snd_pellet = {}
snd_pellet[0] = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sounds","pellet1.wav"))
snd_pellet[1] = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sounds","pellet2.wav"))
snd_powerpellet = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sounds","powerpellet.wav"))
snd_eatgh = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sounds","eatgh2.wav"))
snd_fruitbounce = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sounds","fruitbounce.wav"))
snd_eatfruit = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sounds","eatfruit.wav"))
snd_extralife = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sounds","extralife.wav"))

#CONFIGURACION DEL COLOR DE LOS FANTASMAS
ghostcolor = {}
ghostcolor[0] = (255, 0, 0, 255)
ghostcolor[1] = (255, 128, 255, 255)
ghostcolor[2] = (128, 255, 255, 255)
ghostcolor[3] = (255, 128, 0, 255)
ghostcolor[4] = (50, 50, 255, 255) #azul, fantasma vulnerable
ghostcolor[5] = (255, 255, 255, 255) # blanco, fantasma intermitente

# __________DEFINICION DE CLASES________

# Dentro de la clase game, se definen métodos (funciones asociadas a la clase) y atributos
# (variables asociadas a la clase).

class game ():

# Este método devuelve una lista predeterminada de puntuaciones más altas con nombres asociados.
    def defaulthiscorelist(self):
            return [ (100000,"Dario") , (80000,"Juan") , (60000,"Yuly") , (40000,"Jose") , (20000,"Sulmy") , (10000,"Pepito") ]

#Este método intenta leer un archivo llamado hiscore.txt y devuelve la lista de puntuaciones más altas.
# Si el archivo no existe, devuelve la lista predeterminada.
    def gethiscores(self):
            
            try:
              f=open(os.path.join(SCRIPT_PATH,"res","hiscore.txt"))
              hs=[]
              for line in f:
                while len(line)>0 and (line[0]=="\n" or line[0]=="\r"): line=line[1:]
                while len(line)>0 and (line[-1]=="\n" or line[-1]=="\r"): line=line[:-1]
                score=int(line.split(" ")[0])
                name=line.partition(" ")[2]
                if score>99999999: score=99999999
                if len(name)>22: name=name[:22]
                hs.append((score,name))
              f.close()
              if len(hs)>6: hs=hs[:6]
              while len(hs)<6: hs.append((0,""))
              return hs
            except IOError:
              return self.defaulthiscorelist()
          
# Este método toma una nueva lista de puntuaciones más altas y la escribe en un archivo llamado hiscore.txt.
    def writehiscores(self,hs):
            
            fname=os.path.join(SCRIPT_PATH,"res","hiscore.txt")
            f=open(fname,"w")
            for line in hs:
              f.write(str(line[0])+" "+line[1]+"\n")
            f.close()
            
# Este método solicita al jugador su nombre para agregarlo a la lista de puntuaciones más altas.
    def getplayername(self):
            
            if NO_WX: return USER_NAME
            try:
              import wx
            except:
              print("Error de Pacman: No se encuentra el módulo wx. No se puede solicitar al usuario su nombre!")
              print( " 😥 Descarga wx desde http://www.wxpython.org/")
              print( " 😥 Para evitar ver este error nuevamente, establece NO_WX en el archivo pacman.pyw.")
              return USER_NAME
            app=wx.App(None)
            dlog=wx.TextEntryDialog(None,"Haz la lista de puntuación más alta. Nombre:")
            dlog.ShowModal()
            name=dlog.GetValue()
            dlog.Destroy()
            app.Destroy()
            return name
        
# Este método agrega una nueva puntuación a la lista de puntuaciones más altas si es apropiado.
    def updatehiscores(self,newscore):
            """Add newscore to the high score list, if appropriate."""
            hs=self.gethiscores()
            for line in hs:
              if newscore>=line[0]:
                hs.insert(hs.index(line),(newscore,self.getplayername()))
                hs.pop(-1)
                break
            self.writehiscores(hs)

# Este método lee el archivo de puntuaciones más altas y lo convierte en una superficie utilizable
# para su representación gráfica.
    def makehiscorelist(self):
            "Lee el archivo de puntuación más alta y conviértelo en una superficie utilizable"
            
            f=pygame.font.Font(os.path.join(SCRIPT_PATH,"res","VeraMoBd.ttf"),10)
            scoresurf=pygame.Surface((276,86),pygame.SRCALPHA)
            scoresurf.set_alpha(200)
            linesurf=f.render(" "*18+"HIGH SCORES",1,(255,255,0))
            scoresurf.blit(linesurf,(0,0))
            hs=self.gethiscores()
            vpos=0
            for line in hs:
              vpos+=12
              linesurf=f.render(line[1].rjust(22)+str(line[0]).rjust(9),1,(255,255,255))
              scoresurf.blit(linesurf,(0,vpos))
            return scoresurf
        
# Este método vuelve a dibujar la imagen de la lista de puntuaciones más altas durante el juego después de que Pacman muere.
    def drawmidgamehiscores(self):
            self.imHiscores=self.makehiscorelist()

# Este método especial (__init__) inicializa una instancia de la clase game con valores iniciales.
# En este caso, establece el nivel (levelNum) en 0, la puntuación (score) en 0 y las vidas (lives) en 3.
    def __init__ (self):
        self.levelNum = 0
        self.score = 0
        self.lives = 3
        
# Aquí se establece una serie de variables relacionadas con el estado del juego.
# La variable mode indica el estado actual del juego, como "normal", "golpeó a un fantasma",
# "juego terminado", etc. Se inicializan otras variables relacionadas con temporizadores y posiciones.

        self.mode = 0  # Variable que indica el estado del juego (1 = normal, 2 = golpeó a un fantasma, ...)
        self.modeTimer = 0  # Temporizador asociado al modo de juego actual
        self.ghostTimer = 0  # Temporizador para el comportamiento de los fantasmas
        self.ghostValue = 0  # Valor asociado al estado de vulnerabilidad de los fantasmas
        self.fruitTimer = 0  # Temporizador para la aparición de frutas
        self.fruitScoreTimer = 0  # Temporizador para mostrar la puntuación obtenida al comer frutas
        self.fruitScorePos = (0, 0)  # Posición de la puntuación obtenida al comer frutas

        
        self.SetMode( 3 )
        
        # VARIABLES DE CAMARA
        
        # Estas variables están relacionadas con el seguimiento de la posición de la pantalla y
        # la cámara en el juego. Se definen la posición absoluta de la pantalla en píxeles,
        # la posición de la pantalla más cercana a una baldosa, el desplazamiento en píxeles y
        # el tamaño de la pantalla.
        
        self.screenPixelPos = (0, 0) # posición absoluta x, y de la pantalla desde la esquina superior izquierda del nivel
        self.screenNearestTilePos = (0, 0) # posición de la pantalla más cercana a la baldosa desde la esquina superior izquierda
        self.screenPixelOffset = (0, 0) # desplazamiento en píxeles de la pantalla desde su posición más cercana a la baldosa
        
        self.screenTileSize = (23, 21)
        self.screenSize = (self.screenTileSize[1] * 16, self.screenTileSize[0] * 16)

        # DIGITOS PARA LA PANTALLA NUMERICA
        # cargan imágenes que se utilizan para mostrar dígitos, iconos de vida, mensajes de "Game Over",
        # "Ready", el logo del juego y la lista de puntuaciones más altas.
        self.digit = {}
        for i in range(0, 10, 1):
            self.digit[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text",str(i) + ".gif")).convert()
        self.imLife = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text","life.gif")).convert()
        self.imGameOver = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text","gameover.gif")).convert()
        self.imReady = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text","ready.gif")).convert()
        self.imLogo = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text","logo.gif")).convert()
        self.imHiscores = self.makehiscorelist()
    
    # Este método inicializa un nuevo juego, estableciendo el nivel en 1, la puntuación y
    # las vidas en valores predeterminados, y configurando el modo de juego para
    # "esperar para comenzar". Luego, carga el primer nivel del juego.
    def StartNewGame (self):
        self.levelNum = 1
        self.score = 0
        self.lives = 3
        
        self.SetMode( 4 )
        thisLevel.LoadLevel( thisGame.GetLevelNum() )
        
    # Este método agrega una cantidad específica a la puntuación del juego.
    # Además, verifica si la puntuación alcanza ciertos umbrales predefinidos y
    # otorga una vida extra si es necesario.
    
    def AddToScore (self, amount):
        
        extraLifeSet = [25000, 50000, 100000, 150000]
        
        for specialScore in extraLifeSet:
            if self.score < specialScore and self.score + amount >= specialScore:
                snd_extralife.play()
                thisGame.lives += 1
        
        self.score += amount
        
    # Dibuja en la pantalla la puntuación del jugador, las vidas restantes, la fruta actual, el mensaje de "game over" o "listo", y el número actual del nivel.
    # Utiliza otros métodos como DrawNumber() para mostrar valores numéricos.
    def DrawScore (self):
        self.DrawNumber (self.score, 24 + 16, self.screenSize[1] - 24 )
            
        for i in range(0, self.lives, 1):
            screen.blit (self.imLife, (24 + i * 10 + 16, self.screenSize[1] - 12) )
            
        screen.blit (thisFruit.imFruit[ thisFruit.fruitType ], (4 + 16, self.screenSize[1] - 20) )
            
        if self.mode == 3:
            screen.blit (self.imGameOver, (self.screenSize[0] / 2 - 32, self.screenSize[1] / 2 - 10) )
        elif self.mode == 4:
            screen.blit (self.imReady, (self.screenSize[0] / 2 - 20, self.screenSize[1] / 2 + 12) )
            
        self.DrawNumber (self.levelNum, 0, self.screenSize[1] - 12 )
            
    # Dibuja un valor numérico en la pantalla en las coordenadas especificadas (x, y). 
    # Descompone el número en dígitos individuales y utiliza imágenes de dígitos para representarlos en la pantalla.
    def DrawNumber (self, number, x, y):
        strNumber = str(int(number))
        for i in range(0, len(strNumber), 1):
            iDigit = int(strNumber[i])
            screen.blit (self.digit[ iDigit ], (x + i * 9, y) )
            
    # Determina la nueva posición posible para la pantalla del juego basándose en la posición del jugador.
    # Asegura que la pantalla se mantenga dentro de los límites del nivel del juego.
    def SmartMoveScreen (self):
            
        possibleScreenX = player.x - self.screenTileSize[1] / 2 * 16
        possibleScreenY = player.y - self.screenTileSize[0] / 2 * 16
        
        if possibleScreenX < 0:
            possibleScreenX = 0
        elif possibleScreenX > thisLevel.lvlWidth * 16 - self.screenSize[0]:
            possibleScreenX = thisLevel.lvlWidth * 16 - self.screenSize[0]
            
        if possibleScreenY < 0:
            possibleScreenY = 0
        elif possibleScreenY > thisLevel.lvlHeight * 16 - self.screenSize[1]:
            possibleScreenY = thisLevel.lvlHeight * 16 - self.screenSize[1]
        
        thisGame.MoveScreen( possibleScreenX, possibleScreenY )
        
    # Actualiza la posición de la pantalla del juego.
    # Calcula la posición de la baldosa más cercana de la pantalla y la compensación de píxeles desde
    # esa posición de baldosas.
    def MoveScreen (self, newX, newY ):
        self.screenPixelPos = (newX, newY)
        self.screenNearestTilePos = (int(newY / 16), int(newX / 16)) # nearest-tile position of the screen from the UL corner
        self.screenPixelOffset = (newX - self.screenNearestTilePos[1]*16, newY - self.screenNearestTilePos[0]*16)
    
    # Devuelve la posición actual en píxeles de la pantalla del juego.
    def GetScreenPos (self):
        return self.screenPixelPos
    
    # Devuelve el número actual del nivel.
    def GetLevelNum (self):
        return self.levelNum
    
    # Incrementa el número actual del nivel.
    # Establece el modo de juego en 4 (modo "listo") y carga el siguiente nivel utilizando LoadLevel().
    def SetNextLevel (self):
        self.levelNum += 1
        
        self.SetMode( 4 )
        thisLevel.LoadLevel( thisGame.GetLevelNum() )
        
        player.velX = 0
        player.velY = 0
        player.anim_pacmanCurrent = player.anim_pacmanS
        
    # Este método, SetMode, asigna un nuevo modo de juego (newMode) a la variable de instancia mode y
    # restablece el temporizador del modo a cero.
    def SetMode (self, newMode):
        self.mode = newMode
        self.modeTimer = 0

# Esta clase define una clase llamada node que se utiliza para representar nodos en un algoritmo de
# búsqueda de camino, como A*. Cada nodo tiene atributos que almacenan información sobre los costos
# de movimiento, el nodo padre en el camino, y el tipo de nodo (espacio vacío, pared, inicio o final). 
# Estos atributos son comunes en algoritmos de búsqueda de camino para determinar la ruta óptima
# en un espacio definido.
class node ():
    
    def __init__ (self):
        self.g = -1 # Costo de movimiento para moverse desde el nodo anterior a este (generalmente +10)
        self.h = -1 # Costo estimado de movimiento para moverse desde este nodo al nodo final (pasos restantes horizontal y vertical * 10)
        self.f = -1 # Costo total de movimiento de este nodo (= g + h)
        # Nodo padre
        self.parent = (-1, -1)
        # Tipo de nodo: 0 para espacio vacío, 1 para pared (opcionalmente, 2 para nodo de inicio y 3 para nodo final)
        self.type = -1

#  Se define una clase llamada path_finder que se utiliza para encontrar
# rutas en un mapa bidimensional.

class path_finder ():
    
    # Inicializa la instancia de la clase.
    # Define un mapa y sus dimensiones, variables para almacenar información de la ruta, y
    # configuraciones iniciales.
    def __init__ (self):
        self.map = {}
        self.size = (-1, -1)
        
        self.pathChainRev = ""
        self.pathChain = ""
                
        # nodos inicial y final
        self.start = (-1, -1)
        self.end = (-1, -1)
        
        # nodo actual (utilizado por el algoritmo)
        self.current = (-1, -1)
        
        # listas abiertas y cerradas de nodos a considerar (utilizadas por el algoritmo)
        self.openList = []
        self.closedList = []
        
        # utilizado en el algoritmo (el buscador de rutas de vecinos adyacentes puede tenerlo en cuenta)
        self.neighborSet = [ (0, -1), (0, 1), (-1, 0), (1, 0) ]
        
    # Redimensiona el mapa a las dimensiones especificadas.
    # Inicializa el mapa como una matriz 2D de nodos vacíos.
    def ResizeMap (self, numRows, numCols):
        self.map = {}
        self.size = (numRows, numCols)

        for row in range(0, self.size[0], 1):
            for col in range(0, self.size[1], 1):
                self.Set( row, col, node() )
                self.SetType( row, col, 0 )
                
    # Restablece variables temporales necesarias para una búsqueda, manteniendo el mismo mapa.
    def CleanUpTemp (self):
         
        self.pathChainRev = ""
        self.pathChain = ""
        self.current = (-1, -1)
        self.openList = []
        self.closedList = []
        
    # Encuentra una ruta desde la posición de inicio hasta la posición final utilizando el algoritmo A*.
    # Limpia variables temporales.
    # Inicia la búsqueda, explorando nodos y actualizando costos hasta llegar al nodo final
    # o no encontrar una ruta.
    def FindPath (self, startPos, endPos ):
        
        self.CleanUpTemp()
        
        # (fila, columna) tuplas
        self.start = startPos
        self.end = endPos
        
        # añadir nodo de inicio a lista abierta
        self.AddToOpenList( self.start )
        self.SetG ( self.start, 0 )
        self.SetH ( self.start, 0 )
        self.SetF ( self.start, 0 )
        
        doContinue = True
        
        #Se ejecuta un bucle
        while (doContinue == True):
        
            thisLowestFNode = self.GetLowestFNode()

            if not thisLowestFNode == self.end and not thisLowestFNode == False:
                self.current = thisLowestFNode
                self.RemoveFromOpenList( self.current )
                self.AddToClosedList( self.current )
                
                for offset in self.neighborSet:
                    thisNeighbor = (self.current[0] + offset[0], self.current[1] + offset[1])
                    
                    if not thisNeighbor[0] < 0 and not thisNeighbor[1] < 0 and not thisNeighbor[0] > self.size[0] - 1 and not thisNeighbor[1] > self.size[1] - 1 and not self.GetType( thisNeighbor ) == 1:
                        cost = self.GetG( self.current ) + 10
                        
                        if self.IsInOpenList( thisNeighbor ) and cost < self.GetG( thisNeighbor ):
                            self.RemoveFromOpenList( thisNeighbor )
                                                      
                        if not self.IsInOpenList( thisNeighbor ) and not self.IsInClosedList( thisNeighbor ):
                            self.AddToOpenList( thisNeighbor )
                            self.SetG( thisNeighbor, cost )
                            self.CalcH( thisNeighbor )
                            self.CalcF( thisNeighbor )
                            self.SetParent( thisNeighbor, self.current )
            else:
                doContinue = False
                        
        if thisLowestFNode == False:
            return False
                        
        # RECONSTRUCCION DE LA RUTA
        self.current = self.end
        while not self.current == self.start:
            # Construcción de una representación de cadena de la ruta utilizando R, L, D, U
            if self.current[1] > self.GetParent(self.current)[1]:
                self.pathChainRev += 'R' 
            elif self.current[1] < self.GetParent(self.current)[1]:
                self.pathChainRev += 'L'
            elif self.current[0] > self.GetParent(self.current)[0]:
                self.pathChainRev += 'D'
            elif self.current[0] < self.GetParent(self.current)[0]:
                self.pathChainRev += 'U'
            self.current = self.GetParent(self.current)
            self.SetType( self.current[0],self.current[1], 4)
            
        # because pathChainRev was constructed in reverse order, it needs to be reversed!
        for i in range(len(self.pathChainRev) - 1, -1, -1):
            self.pathChain += self.pathChainRev[i]
        
        # set start and ending positions for future reference
        self.SetType( self.start[0],self.start[1], 2)
        self.SetType( self.end[0],self.start[1], 3)
        
        return self.pathChain
    # Funcion fold Convierte un par de coordenadas 2D (fila, col) en un índice de matriz 1D utilizando una fórmula.
    def Unfold (self, row,col):
        return (row * self.size[1]) + col
    
    # Métodos de Manipulación del Mapa
    # Métodos para manipular el mapa bidimensional, estableciendo y obteniendo tipos y valores asociados a los nodos.
    def Set (self, row,col, newNode):
        self.map[ self.Unfold(row, col) ] = newNode
        
    def GetType (self,val):
        row,col = val
        return self.map[ self.Unfold(row, col) ].type
        
    def SetType (self,row,col, newValue):
        self.map[ self.Unfold(row, col) ].type = newValue

    def GetF (self, val):
        row,col = val
        return self.map[ self.Unfold(row, col) ].f

    def GetG (self, val):
        row,col = val
        return self.map[ self.Unfold(row, col) ].g
    
    def GetH (self, val):
        row,col = val
        return self.map[ self.Unfold(row, col) ].h
        
    def SetG (self, val, newValue ):
        row,col = val
        self.map[ self.Unfold(row, col) ].g = newValue

    def SetH (self, val, newValue ):
        row,col = val
        self.map[ self.Unfold(row, col) ].h = newValue
        
    def SetF (self, val, newValue ):
        row,col = val
        self.map[ self.Unfold(row, col) ].f = newValue
        
    def CalcH (self, val):
        row,col = val
        self.map[ self.Unfold(row, col) ].h = abs(row - self.end[0]) + abs(col - self.end[0])
        
    def CalcF (self, val):
        row,col = val
        unfoldIndex = self.Unfold(row, col)
        self.map[unfoldIndex].f = self.map[unfoldIndex].g + self.map[unfoldIndex].h
    
    # Métodos de Listas Abiertas y Cerradas: Métodos para manipular la lista abierta, añadiendo,
    # eliminando y verificando si un nodo está en la lista abierta.
    def AddToOpenList (self, val):
        row,col = val
        self.openList.append( (row, col) )
        
    def RemoveFromOpenList (self, val ):
        row,col = val
        self.openList.remove( (row, col) )
        
    def IsInOpenList (self, val ):
        row,col = val
        if self.openList.count( (row, col) ) > 0:
            return True
        else:
            return False
        
    # Función GetLowestFNode
    def GetLowestFNode (self):
        lowestValue = 1000 
        lowestPair = (-1, -1)
        
        for iOrderedPair in self.openList:
            if self.GetF( iOrderedPair ) < lowestValue:
                lowestValue = self.GetF( iOrderedPair )
                lowestPair = iOrderedPair
        
        if not lowestPair == (-1, -1):
            return lowestPair
        else:
            return False
        
    # Funciones de Gestión de Listas y Padres
    
    # AddToClosedList: Agrega una posición a la lista cerrada (closedList).
    def AddToClosedList (self, val ):
        row,col = val
        self.closedList.append( (row, col) )
        
    def IsInClosedList (self, val ):
        row,col = val
        if self.closedList.count( (row, col) ) > 0:
            return True
        else:
            return False

    def SetParent (self, val, val2 ):
        row,col = val
        parentRow,parentCol = val2
        self.map[ self.Unfold(row, col) ].parent = (parentRow, parentCol)

    def GetParent (self, val ):
        row,col = val
        return self.map[ self.Unfold(row, col) ].parent
    
    # Método draw de la Clase path_finder: Dibuja el mapa en la pantalla utilizando imágenes
    # correspondientes a los tipos de baldosas.
    def draw (self):
        for row in range(0, self.size[0], 1):
            for col in range(0, self.size[1], 1):
            
                thisTile = self.GetType((row, col))
                screen.blit (tileIDImage[ thisTile ], (col * 32, row * 32))

#CLASE GHOST (FANTASMA)
# Definición de la clase ghost que representa a un fantasma en el juego.
# Inicialización de atributos como posición, velocidad, estado, animaciones, etc.
class ghost ():
    def __init__ (self, ghostID):
        self.x = 0
        self.y = 0
        self.velX = 0
        self.velY = 0
        self.speed = 1
        
        self.nearestRow = 0
        self.nearestCol = 0
        
        self.id = ghostID
        
        self.state = 1
        
        self.homeX = 0
        self.homeY = 0
        
        self.currentPath = ""
        
        # DICCIONARIO (self.anim)
        self.anim = {}
        for i in range(1, 7, 1):
            self.anim[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","ghost " + str(i) + ".gif")).convert()
            
            for y in range(0, 16, 1):
                for x in range(0, 16, 1):
                
                    if self.anim[i].get_at( (x, y) ) == (255, 0, 0, 255):
                        self.anim[i].set_at( (x, y), ghostcolor[ self.id ] )
            
        self.animFrame = 1
        self.animDelay = 0
    
    # METODO DRAW
    # El método Draw se encarga de dibujar el fantasma en la pantalla.
    # Se ajusta el color de los ojos del fantasma según la posición de Pac-Man.
    # El cuerpo del fantasma se dibuja según su estado (normal, vulnerable o con gafas).
    # Se evita la animación del fantasma si el nivel está completo.
    # Se implementa lógica para la animación del fantasma.
    
    def Draw (self):
        
        if thisGame.mode == 3:
            return False
        
        
        # Dibujo de los ojos del fantasma
        for y in range(4, 8, 1):
            for x in range(3, 7, 1):
                self.anim[ self.animFrame ].set_at( (x, y), (255, 255, 255, 255) )  
                self.anim[ self.animFrame ].set_at( (x+6, y), (255, 255, 255, 255) )
                
                if player.x > self.x and player.y > self.y:
                    pupilSet = (5, 6)
                elif player.x < self.x and player.y > self.y:
                    pupilSet = (3, 6)
                elif player.x > self.x and player.y < self.y:
                    pupilSet = (5, 4)
                elif player.x < self.x and player.y < self.y:
                    pupilSet = (3, 4)
                else:
                    pupilSet = (4, 6)
                    
        for y in range(pupilSet[1], pupilSet[1] + 2, 1):
            for x in range(pupilSet[0], pupilSet[0] + 2, 1):
                self.anim[ self.animFrame ].set_at( (x, y), (0, 0, 255, 255) )  
                self.anim[ self.animFrame ].set_at( (x+6, y), (0, 0, 255, 255) )    
       
        if self.state == 1:
            screen.blit (self.anim[ self.animFrame ], (self.x - thisGame.screenPixelPos[0], self.y - thisGame.screenPixelPos[1]))
        elif self.state == 2:
            
            if thisGame.ghostTimer > 100:
                screen.blit (ghosts[4].anim[ self.animFrame ], (self.x - thisGame.screenPixelPos[0], self.y - thisGame.screenPixelPos[1]))
            else:
                tempTimerI = int(thisGame.ghostTimer / 10)
                if tempTimerI == 1 or tempTimerI == 3 or tempTimerI == 5 or tempTimerI == 7 or tempTimerI == 9:
                    screen.blit (ghosts[5].anim[ self.animFrame ], (self.x - thisGame.screenPixelPos[0], self.y - thisGame.screenPixelPos[1]))
                else:
                    screen.blit (ghosts[4].anim[ self.animFrame ], (self.x - thisGame.screenPixelPos[0], self.y - thisGame.screenPixelPos[1]))
            
        elif self.state == 3:
            screen.blit (tileIDImage[ tileID[ 'glasses' ] ], (self.x - thisGame.screenPixelPos[0], self.y - thisGame.screenPixelPos[1]))
        
        if thisGame.mode == 6 or thisGame.mode == 7:
            return False
        
        # LOGICA PARA ANIMAR AL FANTASMA
        self.animDelay += 1
        
        if self.animDelay == 2:
            self.animFrame += 1 
        
            if self.animFrame == 7:
                # wrap to beginning
                self.animFrame = 1
                
            self.animDelay = 0
    
    # METODO "MOVE"
    # El método Move actualiza la posición del fantasma.
    # Calcula la fila y columna más cercanas en la cuadrícula.
    # Si el fantasma está alineado con la cuadrícula, avanza al siguiente punto del camino.
    # Si no hay más puntos en el camino, calcula un nuevo camino hacia Pac-Man y sigue el próximo camino.
    
    def Move (self):
        

        self.x += self.velX
        self.y += self.velY
        
        self.nearestRow = int(((self.y + 8) / 16))
        self.nearestCol = int(((self.x + 8) / 16))

        if (self.x % 16) == 0 and (self.y % 16) == 0:
            
            if (self.currentPath):
                self.currentPath = self.currentPath[1:]
                self.FollowNextPathWay()
        
            else:
                self.x = self.nearestCol * 16
                self.y = self.nearestRow * 16
            
                # chase pac-man
                self.currentPath = path.FindPath( (self.nearestRow, self.nearestCol), (player.nearestRow, player.nearestCol) )
                self.FollowNextPathWay()
    
    # Método FollowNextPathWay
    def FollowNextPathWay (self):
        
        # El método FollowNextPathWay se encarga de determinar la dirección del siguiente paso en el
        # camino que debe seguir el fantasma.
        
        # Si hay un camino posible, ajusta la velocidad del fantasma en la dirección adecuada.
        
        # Si el fantasma ha llegado a su destino, determina si debe perseguir a Pac-Man o
        # encontrar el camino de regreso a la caja de fantasmas.

        if not self.currentPath == False:
        
            if len(self.currentPath) > 0:
                if self.currentPath[0] == "L":
                    (self.velX, self.velY) = (-self.speed, 0)
                elif self.currentPath[0] == "R":
                    (self.velX, self.velY) = (self.speed, 0)
                elif self.currentPath[0] == "U":
                    (self.velX, self.velY) = (0, -self.speed)
                elif self.currentPath[0] == "D":
                    (self.velX, self.velY) = (0, self.speed)
                    
            else:
                
                if not self.state == 3:
                    # chase pac-man
                    self.currentPath = path.FindPath( (self.nearestRow, self.nearestCol), (player.nearestRow, player.nearestCol) )
                    self.FollowNextPathWay()
                
                else:
                    self.state = 1
                    self.speed = self.speed / 4
                    
                    (randRow, randCol) = (0, 0)

                    while not thisLevel.GetMapTile(randRow, randCol) == tileID[ 'pellet' ] or (randRow, randCol) == (0, 0):
                        randRow = random.randint(1, thisLevel.lvlHeight - 2)
                        randCol = random.randint(1, thisLevel.lvlWidth - 2)

                    self.currentPath = path.FindPath( (self.nearestRow, self.nearestCol), (randRow, randCol) )
                    self.FollowNextPathWay()
                    
# CLASE FRUTA

# La clase fruit representa una fruta en el juego.
# El método Draw se encarga de dibujar la fruta en la pantalla si está activa.
# El método Move se encarga de mover la fruta en la pantalla y gestionar la animación de rebote.
# La fruta tiene atributos como posición, velocidad, estado de actividad, etc.

class fruit ():
    def __init__ (self):
        self.slowTimer = 0
        self.x = -16
        self.y = -16
        self.velX = 0
        self.velY = 0
        self.speed = 1
        self.active = False
        
        self.bouncei = 0
        self.bounceY = 0
        
        self.nearestRow = (-1, -1)
        self.nearestCol = (-1, -1)
        
        self.imFruit = {}
        for i in range(0, 5, 1):
            self.imFruit[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","fruit " + str(i) + ".gif")).convert()
        
        self.currentPath = ""
        self.fruitType = 1
        
    def Draw (self):
        
        if thisGame.mode == 3 or self.active == False:
            return False
        
        screen.blit (self.imFruit[ self.fruitType ], (self.x - thisGame.screenPixelPos[0], self.y - thisGame.screenPixelPos[1] - self.bounceY))

            
    def Move (self):
        
        if self.active == False:
            return False
        
        self.bouncei += 1
        if self.bouncei == 1:
            self.bounceY = 2
        elif self.bouncei == 2:
            self.bounceY = 4
        elif self.bouncei == 3:
            self.bounceY = 5
        elif self.bouncei == 4:
            self.bounceY = 5
        elif self.bouncei == 5:
            self.bounceY = 6
        elif self.bouncei == 6:
            self.bounceY = 6
        elif self.bouncei == 9:
            self.bounceY = 6
        elif self.bouncei == 10:
            self.bounceY = 5
        elif self.bouncei == 11:
            self.bounceY = 5
        elif self.bouncei == 12:
            self.bounceY = 4
        elif self.bouncei == 13:
            self.bounceY = 3
        elif self.bouncei == 14:
            self.bounceY = 2
        elif self.bouncei == 15:
            self.bounceY = 1
        elif self.bouncei == 16:
            self.bounceY = 0
            self.bouncei = 0
            snd_fruitbounce.play()
        
        self.slowTimer += 1
        if self.slowTimer == 2:
            self.slowTimer = 0
            
            self.x += self.velX
            self.y += self.velY
            
            self.nearestRow = int(((self.y + 8) / 16))
            self.nearestCol = int(((self.x + 8) / 16))

            if (self.x % 16) == 0 and (self.y % 16) == 0:

                
                if len(self.currentPath) > 0:
                    self.currentPath = self.currentPath[1:]
                    self.FollowNextPathWay()
            
                else:
                    self.x = self.nearestCol * 16
                    self.y = self.nearestRow * 16
                    
                    self.active = False
                    thisGame.fruitTimer = 0
    
    # Método FollowNextPathWay en la clase ghost:
    
    # Este método se encarga de seguir el siguiente paso en el camino establecido para el fantasma.
    # Verifica si hay un camino actual (currentPath) disponible.
    
    # Si hay elementos en el camino, ajusta la velocidad del fantasma según el primer elemento
    # del camino (L, R, U, D).
    
    # Este método se utiliza para guiar el movimiento del fantasma a lo largo de un camino predeterminado.
    
    def FollowNextPathWay (self):
        

        if not self.currentPath == False:
        
            if len(self.currentPath) > 0:
                if self.currentPath[0] == "L":
                    (self.velX, self.velY) = (-self.speed, 0)
                elif self.currentPath[0] == "R":
                    (self.velX, self.velY) = (self.speed, 0)
                elif self.currentPath[0] == "U":
                    (self.velX, self.velY) = (0, -self.speed)
                elif self.currentPath[0] == "D":
                    (self.velX, self.velY) = (0, self.speed)

# CLASE PACMAN

# Representa al personaje principal, Pac-Man, en el juego.

# El constructor (__init__) inicializa las propiedades del objeto Pac-Man, como posición, velocidad y animaciones.

class pacman ():
    
    def __init__ (self):
        self.x = 0
        self.y = 0
        self.velX = 0
        self.velY = 0
        self.speed = 2
        
        self.nearestRow = 0
        self.nearestCol = 0
        
        self.homeX = 0
        self.homeY = 0
        
        self.anim_pacmanL = {}
        self.anim_pacmanR = {}
        self.anim_pacmanU = {}
        self.anim_pacmanD = {}
        self.anim_pacmanS = {}
        self.anim_pacmanCurrent = {}
        
        for i in range(1, 9, 1):
            self.anim_pacmanL[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","pacman-l " + str(i) + ".gif")).convert()
            self.anim_pacmanR[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","pacman-r " + str(i) + ".gif")).convert()
            self.anim_pacmanU[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","pacman-u " + str(i) + ".gif")).convert()
            self.anim_pacmanD[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","pacman-d " + str(i) + ".gif")).convert()
            self.anim_pacmanS[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","pacman.gif")).convert()

        self.pelletSndNum = 0
    
    # El método Move gestiona el movimiento de Pac-Man, asegurándose de que no choque con las paredes,
    # gestionando colisiones con otros elementos del juego y actualizando temporizadores.
    def Move (self):
        
        self.nearestRow = int(((self.y + 8) / 16))
        self.nearestCol = int(((self.x + 8) / 16))

        if not thisLevel.CheckIfHitWall(self.x + self.velX, self.y + self.velY, self.nearestRow, self.nearestCol):
            # it's ok to Move
            self.x += self.velX
            self.y += self.velY
            
            thisLevel.CheckIfHitSomething(self.x, self.y, self.nearestRow, self.nearestCol)
            
            for i in range(0, 4, 1):
                if thisLevel.CheckIfHit( self.x, self.y, ghosts[i].x, ghosts[i].y, 8):
                    
                    if ghosts[i].state == 1:
                        thisGame.SetMode( 2 )
                        
                    elif ghosts[i].state == 2:

                        thisGame.AddToScore(thisGame.ghostValue)
                        thisGame.ghostValue = thisGame.ghostValue * 2
                        snd_eatgh.play()
                        
                        ghosts[i].state = 3
                        ghosts[i].speed = ghosts[i].speed * 4
                        # and send them to the ghost box
                        ghosts[i].x = ghosts[i].nearestCol * 16
                        ghosts[i].y = ghosts[i].nearestRow * 16
                        ghosts[i].currentPath = path.FindPath( (ghosts[i].nearestRow, ghosts[i].nearestCol), (thisLevel.GetGhostBoxPos()[0]+1, thisLevel.GetGhostBoxPos()[1]) )
                        ghosts[i].FollowNextPathWay()
                        
                        # establecer el modo de juego en una breve pausa después de comer
                        thisGame.SetMode( 5 )
                        
            # verificar colisiones con la fruta
            if thisFruit.active == True:
                if thisLevel.CheckIfHit( self.x, self.y, thisFruit.x, thisFruit.y, 8):
                    thisGame.AddToScore(2500)
                    thisFruit.active = False
                    thisGame.fruitTimer = 0
                    thisGame.fruitScoreTimer = 120
                    snd_eatfruit.play()
        
        else:
            # Nos vamos a chocar con una pared, así que dejamos de movernos.
            self.velX = 0
            self.velY = 0
            
        # Manejar el temporizador de los fantasmas con power-pellet.
        if thisGame.ghostTimer > 0:
            thisGame.ghostTimer -= 1
            
            if thisGame.ghostTimer == 0:
                for i in range(0, 4, 1):
                    if ghosts[i].state == 2:
                        ghosts[i].state = 1
                self.ghostValue = 0
                
        # Manejar el temporizador de la fruta.
        thisGame.fruitTimer += 1
        if thisGame.fruitTimer == 500:
            pathwayPair = thisLevel.GetPathwayPairPos()
            
            if not pathwayPair == False:
            
                pathwayEntrance = pathwayPair[0]
                pathwayExit = pathwayPair[1]
                
                thisFruit.active = True
                
                thisFruit.nearestRow = pathwayEntrance[0]
                thisFruit.nearestCol = pathwayEntrance[1]
                
                thisFruit.x = thisFruit.nearestCol * 16
                thisFruit.y = thisFruit.nearestRow * 16
                
                thisFruit.currentPath = path.FindPath( (thisFruit.nearestRow, thisFruit.nearestCol), pathwayExit )
                thisFruit.FollowNextPathWay()
            
        if thisGame.fruitScoreTimer > 0:
            thisGame.fruitScoreTimer -= 1
            
    # El método Draw dibuja la animación de Pac-Man en la pantalla, seleccionando la dirección adecuada
    # según la velocidad.
    def Draw (self):
        
        if thisGame.mode == 3:
            return False
        
        # Establecer el array del cuadro actual para que coincida con la dirección hacia la que Pacman está mirando.
        if self.velX > 0:
            self.anim_pacmanCurrent = self.anim_pacmanR
        elif self.velX < 0:
            self.anim_pacmanCurrent = self.anim_pacmanL
        elif self.velY > 0:
            self.anim_pacmanCurrent = self.anim_pacmanD
        elif self.velY < 0:
            self.anim_pacmanCurrent = self.anim_pacmanU
            
        screen.blit (self.anim_pacmanCurrent[ self.animFrame ], (self.x - thisGame.screenPixelPos[0], self.y - thisGame.screenPixelPos[1]))
        
        if thisGame.mode == 1:
            if not self.velX == 0 or not self.velY == 0:
                # Mover solo la boca cuando Pacman se está moviendo.
                self.animFrame += 1 
            
            if self.animFrame == 9:
                # wrap to beginning
                self.animFrame = 1

#CLASE LEVEL
# Representa un nivel del juego.
# El constructor (__init__) inicializa propiedades relacionadas con el diseño del nivel y los colores.
# SetMapTile y GetMapTile son métodos para establecer y obtener el tipo de casilla en una posición específica del mapa, respectivamente.   

class level ():
    
    def __init__ (self):
        self.lvlWidth = 0
        self.lvlHeight = 0
        self.edgeLightColor = (255, 255, 0, 255)
        self.edgeShadowColor = (255, 150, 0, 255)
        self.fillColor = (0, 255, 255, 255)
        self.pelletColor = (255, 255, 255, 255)
        
        self.map = {}
        
        self.pellets = 0
        self.powerPelletBlinkTimer = 0
        
    def SetMapTile (self, row, col, newValue):
        self.map[ (row * self.lvlWidth) + col ] = newValue
        
    def GetMapTile (self, row, col):
        if row >= 0 and row < self.lvlHeight and col >= 0 and col < self.lvlWidth:
            return self.map[ (row * self.lvlWidth) + col ]
        else:
            return 0
        
    # La función IsWall verifica si una posición dada en el laberinto es una pared. Utiliza la función
    # GetMapTile para obtener el ID del mosaico en esa posición y determina si corresponde a una
    # pared según un rango específico de ID de mosaico.
    
    def IsWall (self, row, col):
    
        if row > thisLevel.lvlHeight - 1 or row < 0:
            return True
        
        if col > thisLevel.lvlWidth - 1 or col < 0:
            return True
    
        # check the offending tile ID
        result = thisLevel.GetMapTile(row, col)

        # if the tile was a wall
        if result >= 100 and result <= 199:
            return True
        else:
            return False
    
    # La función CheckIfHitWall verifica si el jugador, en una posible nueva posición,
    # colisionará con una pared en su entorno. Examina las posiciones circundantes al jugador y
    # utiliza la función IsWall para determinar si hay colisiones.
    
    def CheckIfHitWall (self, possiblePlayerX, possiblePlayerY, row, col):
    
        numCollisions = 0
        
        # check each of the 9 surrounding tiles for a collision
        for iRow in range(row - 1, row + 2, 1):
            for iCol in range(col - 1, col + 2, 1):
            
                if  (possiblePlayerX - (iCol * 16) < 16) and (possiblePlayerX - (iCol * 16) > -16) and (possiblePlayerY - (iRow * 16) < 16) and (possiblePlayerY - (iRow * 16) > -16):
                    
                    if self.IsWall(iRow, iCol):
                        numCollisions += 1
                        
        if numCollisions > 0:
            return True
        else:
            return False
        
    #La función CheckIfHit verifica si hay una colisión entre dos entidades, como el jugador y
    # un objeto en el juego, dentro de un área determinada definida por el parámetro "cushion".
    
    def CheckIfHit (self, playerX, playerY, x, y, cushion):
    
        if (playerX - x < cushion) and (playerX - x > -cushion) and (playerY - y < cushion) and (playerY - y > -cushion):
            return True
        else:
            return False

    # La función CheckIfHitSomething verifica si el jugador ha golpeado algo en su entorno
    # inmediato, como pellets. Examina las posiciones circundantes al jugador y realiza acciones
    # específicas según el tipo de mosaico en esas posiciones.
    
    def CheckIfHitSomething (self, playerX, playerY, row, col):
    
        for iRow in range(row - 1, row + 2, 1):
            for iCol in range(col - 1, col + 2, 1):
            
                if  (playerX - (iCol * 16) < 16) and (playerX - (iCol * 16) > -16) and (playerY - (iRow * 16) < 16) and (playerY - (iRow * 16) > -16):
                    result = thisLevel.GetMapTile(iRow, iCol)
        
                    if result == tileID[ 'pellet' ]:
                        thisLevel.SetMapTile(iRow, iCol, 0)
                        snd_pellet[player.pelletSndNum].play()
                        player.pelletSndNum = 1 - player.pelletSndNum
                        
                        thisLevel.pellets -= 1
                        
                        thisGame.AddToScore(10)
                        
                        if thisLevel.pellets == 0:
                            thisGame.SetMode( 6 )
                            
                        
                    elif result == tileID[ 'pellet-power' ]:
                        thisLevel.SetMapTile(iRow, iCol, 0)
                        snd_powerpellet.play()
                        
                        thisGame.AddToScore(100)
                        thisGame.ghostValue = 200
                        
                        thisGame.ghostTimer = 360
                        for i in range(0, 4, 1):
                            if ghosts[i].state == 1:
                                ghosts[i].state = 2
                        
                    elif result == tileID[ 'door-h' ]:
                        # Chocó contra una puerta horizontal
                        for i in range(0, thisLevel.lvlWidth, 1):
                            if not i == iCol:
                                if thisLevel.GetMapTile(iRow, i) == tileID[ 'door-h' ]:
                                    player.x = i * 16
                                    
                                    if player.velX > 0:
                                        player.x += 16
                                    else:
                                        player.x -= 16
                                        
                    elif result == tileID[ 'door-v' ]:
                        # Chocó contra una puerta vertical
                        for i in range(0, thisLevel.lvlHeight, 1):
                            if not i == iRow:
                                if thisLevel.GetMapTile(i, iCol) == tileID[ 'door-v' ]:
                                    player.y = i * 16
                                    
                                    if player.velY > 0:
                                        player.y += 16
                                    else:
                                        player.y -= 16
    
    # La función GetGhostBoxPos encuentra la posición del "ghost door" (puerta de los fantasmas)
    # en el laberinto y devuelve las coordenadas de esa posición.    
                             
    def GetGhostBoxPos (self):
        
        for row in range(0, self.lvlHeight, 1):
            for col in range(0, self.lvlWidth, 1):
                if self.GetMapTile(row, col) == tileID[ 'ghost-door' ]:
                    return (row, col)
                
        return False
    
    # GetPathwayPairPos
# Obtiene las posiciones de dos puntos en el laberinto que están asociados como puertas,
# tanto horizontal como verticalmente.

# Utiliza una lista (doorArray) para almacenar las posiciones de las puertas.

# Selecciona aleatoriamente una puerta de la lista y busca la puerta opuesta en la
# dirección opuesta. Devuelve un par de posiciones.

    def GetPathwayPairPos (self):
        
        doorArray = []
        
        for row in range(0, self.lvlHeight, 1):
            for col in range(0, self.lvlWidth, 1):
                if self.GetMapTile(row, col) == tileID[ 'door-h' ]:
                    # Encontro una puerta horizontal
                    doorArray.append( (row, col) )
                elif self.GetMapTile(row, col) == tileID[ 'door-v' ]:
                    # Encontro una puerta vertical
                    doorArray.append( (row, col) )
        
        if len(doorArray) == 0:
            return False
        
        chosenDoor = random.randint(0, len(doorArray) - 1)
        
        if self.GetMapTile( doorArray[chosenDoor][0],doorArray[chosenDoor][1] ) == tileID[ 'door-h' ]:
            for i in range(0, thisLevel.lvlWidth, 1):
                if not i == doorArray[chosenDoor][1]:
                    if thisLevel.GetMapTile(doorArray[chosenDoor][0], i) == tileID[ 'door-h' ]:
                        return doorArray[chosenDoor], (doorArray[chosenDoor][0], i)
        else:
            for i in range(0, thisLevel.lvlHeight, 1):
                if not i == doorArray[chosenDoor][0]:
                    if thisLevel.GetMapTile(i, doorArray[chosenDoor][1]) == tileID[ 'door-v' ]:
                        return doorArray[chosenDoor], (i, doorArray[chosenDoor][1])
                    
        return False
    
    # PrintMap
    # Imprime el contenido del mapa en la consola.
    # No utiliza estructuras de datos complejas, solo bucles y variables locales.
    
    def PrintMap (self):
        
        for row in range(0, self.lvlHeight, 1):
            outputLine = ""
            for col in range(0, self.lvlWidth, 1):
            
                outputLine += str( self.GetMapTile(row, col) ) + ", "
                
    # DrawMap
    
    # Dibuja el mapa en la pantalla de juego.
    # Usa bucles para iterar sobre las posiciones del mapa y dibuja las imágenes correspondientes en la pantalla.
    # Tiene un temporizador (powerPelletBlinkTimer) que alterna el dibujo de pellets de poder.
    
    def DrawMap (self):
        
        self.powerPelletBlinkTimer += 1
        if self.powerPelletBlinkTimer == 60:
            self.powerPelletBlinkTimer = 0
        
        for row in range(-1, thisGame.screenTileSize[0] +1, 1):
            outputLine = ""
            for col in range(-1, thisGame.screenTileSize[1] +1, 1):

                # row containing tile that actually goes here
                actualRow = thisGame.screenNearestTilePos[0] + row
                actualCol = thisGame.screenNearestTilePos[1] + col

                useTile = self.GetMapTile(actualRow, actualCol)
                if not useTile == 0 and not useTile == tileID['door-h'] and not useTile == tileID['door-v']:
                    # if this isn't a blank tile

                    if useTile == tileID['pellet-power']:
                        if self.powerPelletBlinkTimer < 30:
                            screen.blit (tileIDImage[ useTile ], (col * 16 - thisGame.screenPixelOffset[0], row * 16 - thisGame.screenPixelOffset[1]) )

                    elif useTile == tileID['showlogo']:
                        screen.blit (thisGame.imLogo, (col * 16 - thisGame.screenPixelOffset[0], row * 16 - thisGame.screenPixelOffset[1]) )
                    
                    elif useTile == tileID['hiscores']:
                            screen.blit(thisGame.imHiscores,(col*16-thisGame.screenPixelOffset[0],row*16-thisGame.screenPixelOffset[1]))
                    
                    else:
                        screen.blit (tileIDImage[ useTile ], (col * 16 - thisGame.screenPixelOffset[0], row * 16 - thisGame.screenPixelOffset[1]) )
    
    # LoadLevel
    
    # Carga un nivel desde un archivo de texto.
    
    # Utiliza diccionarios (tileID, tileIDImage), listas (str_splitBySpace), y
    # bucles para procesar y cargar datos del nivel.
    
    # Lee y procesa líneas del archivo para determinar el tamaño del nivel,
    # colores, ubicación de objetos y posición de inicio de personajes.
    
    def LoadLevel (self, levelNum):
        
        self.map = {}
        
        self.pellets = 0
        
        f = open(os.path.join(SCRIPT_PATH,"res","levels",str(levelNum) + ".txt"), 'r')
        lineNum=-1
        rowNum = 0
        useLine = False
        isReadingLevelData = False
          
        for line in f:

          lineNum += 1
        
          while len(line)>0 and (line[-1]=="\n" or line[-1]=="\r"): line=line[:-1]
          while len(line)>0 and (line[0]=="\n" or line[0]=="\r"): line=line[1:]
          str_splitBySpace = line.split(' ')
            
            
          j = str_splitBySpace[0]
                
          if (j == "'" or j == ""):
                useLine = False
          elif j == "#":
                useLine = False
                
                firstWord = str_splitBySpace[1]
                
                if firstWord == "lvlwidth":
                    self.lvlWidth = int( str_splitBySpace[2] )
                    
                elif firstWord == "lvlheight":
                    self.lvlHeight = int( str_splitBySpace[2] )
                    
                elif firstWord == "edgecolor":
                    red = int( str_splitBySpace[2] )
                    green = int( str_splitBySpace[3] )
                    blue = int( str_splitBySpace[4] )
                    self.edgeLightColor = (red, green, blue, 255)
                    self.edgeShadowColor = (red, green, blue, 255)
                    
                elif firstWord == "edgelightcolor":
                    red = int( str_splitBySpace[2] )
                    green = int( str_splitBySpace[3] )
                    blue = int( str_splitBySpace[4] )
                    self.edgeLightColor = (red, green, blue, 255)
                    
                elif firstWord == "edgeshadowcolor":
                    red = int( str_splitBySpace[2] )
                    green = int( str_splitBySpace[3] )
                    blue = int( str_splitBySpace[4] )
                    self.edgeShadowColor = (red, green, blue, 255)
                
                elif firstWord == "fillcolor":
                    red = int( str_splitBySpace[2] )
                    green = int( str_splitBySpace[3] )
                    blue = int( str_splitBySpace[4] )
                    self.fillColor = (red, green, blue, 255)
                    
                elif firstWord == "pelletcolor":
                    red = int( str_splitBySpace[2] )
                    green = int( str_splitBySpace[3] )
                    blue = int( str_splitBySpace[4] )
                    self.pelletColor = (red, green, blue, 255)
                    
                elif firstWord == "fruittype":
                    thisFruit.fruitType = int( str_splitBySpace[2] )
                    
                elif firstWord == "startleveldata":
                    isReadingLevelData = True
                    rowNum = 0
                    
                elif firstWord == "endleveldata":
                    isReadingLevelData = False
                    
          else:
                useLine = True
                
                
            # Datos de mapa
          if useLine == True:
                
                if isReadingLevelData == True:
                        
                    
                    for k in range(0, self.lvlWidth, 1):
                        self.SetMapTile(rowNum, k, int(str_splitBySpace[k]) )
                        
                        thisID = int(str_splitBySpace[k])
                        if thisID == 4: 
                            
                            player.homeX = k * 16
                            player.homeY = rowNum * 16
                            self.SetMapTile(rowNum, k, 0 )
                            
                        elif thisID >= 10 and thisID <= 13:
                            
                            ghosts[thisID - 10].homeX = k * 16
                            ghosts[thisID - 10].homeY = rowNum * 16
                            self.SetMapTile(rowNum, k, 0 )
                        
                        elif thisID == 2:
                            
                            self.pellets += 1
                            
                    rowNum += 1
                    
                
        GetCrossRef()

        # Carga el mapa en el objeto de búsqueda de ruta.
        path.ResizeMap( self.lvlHeight, self.lvlWidth )
        
        for row in range(0, path.size[0], 1):
            for col in range(0, path.size[1], 1):
                if self.IsWall( row, col ):
                    path.SetType( row, col, 1 )
                else:
                    path.SetType( row, col, 0 )
        
        # Realiza todas las acciones de inicio del nivel.
        self.Restart()
    
    # Restart
    
    # Reinicia el estado del juego y coloca a los personajes en sus posiciones iniciales.
    # Utiliza bucles para reiniciar las posiciones de fantasmas y jugadores.
    # Asigna posiciones iniciales a los personajes y configura sus estados iniciales.
    
    def Restart (self):
        
        for i in range(0, 4, 1):
            # Mueve a los fantasmas de vuelta a su posición inicial.

            ghosts[i].x = ghosts[i].homeX
            ghosts[i].y = ghosts[i].homeY
            ghosts[i].velX = 0
            ghosts[i].velY = 0
            ghosts[i].state = 1
            ghosts[i].speed = 1
            ghosts[i].Move()
            
            # Da a cada fantasma un camino hacia un lugar aleatorio
            (randRow, randCol) = (0, 0)

            while not self.GetMapTile(randRow, randCol) == tileID[ 'pellet' ] or (randRow, randCol) == (0, 0):
                randRow = random.randint(1, self.lvlHeight - 2)
                randCol = random.randint(1, self.lvlWidth - 2)
            
            ghosts[i].currentPath = path.FindPath( (ghosts[i].nearestRow, ghosts[i].nearestCol), (randRow, randCol) )
            ghosts[i].FollowNextPathWay()
            
        thisFruit.active = False
            
        thisGame.fruitTimer = 0

        player.x = player.homeX
        player.y = player.homeY
        player.velX = 0
        player.velY = 0
        
        player.anim_pacmanCurrent = player.anim_pacmanS
        player.animFrame = 3

# CheckIfCloseButton
# Verifica si se ha cerrado la ventana del juego.
# Utiliza eventos de Pygame para verificar si se ha cerrado la ventana.

def CheckIfCloseButton(events):
    for event in events: 
        if event.type == pygame.QUIT: 
            sys.exit(0)

# CheckInputs

# Maneja las entradas del jugador.
# Verifica las teclas presionadas y ajusta la velocidad del jugador en consecuencia.
# También maneja eventos de joystick.
# Utiliza estructuras condicionales y eventos de Pygame.

def CheckInputs(): 
    
    if thisGame.mode == 1:
        if pygame.key.get_pressed()[ pygame.K_RIGHT ] or (js!=None and js.get_axis(JS_XAXIS)>0):
            if not thisLevel.CheckIfHitWall(player.x + player.speed, player.y, player.nearestRow, player.nearestCol): 
                player.velX = player.speed
                player.velY = 0
                
        elif pygame.key.get_pressed()[ pygame.K_LEFT ] or (js!=None and js.get_axis(JS_XAXIS)<0):
            if not thisLevel.CheckIfHitWall(player.x - player.speed, player.y, player.nearestRow, player.nearestCol): 
                player.velX = -player.speed
                player.velY = 0
            
        elif pygame.key.get_pressed()[ pygame.K_DOWN ] or (js!=None and js.get_axis(JS_YAXIS)>0):
            if not thisLevel.CheckIfHitWall(player.x, player.y + player.speed, player.nearestRow, player.nearestCol): 
                player.velX = 0
                player.velY = player.speed
            
        elif pygame.key.get_pressed()[ pygame.K_UP ] or (js!=None and js.get_axis(JS_YAXIS)<0):
            if not thisLevel.CheckIfHitWall(player.x, player.y - player.speed, player.nearestRow, player.nearestCol):
                player.velX = 0
                player.velY = -player.speed
                
    if pygame.key.get_pressed()[ pygame.K_ESCAPE ]:
        sys.exit(0)
            
    elif thisGame.mode == 3:
        if pygame.key.get_pressed()[ pygame.K_RETURN ] or (js!=None and js.get_button(JS_STARTBUTTON)):
            thisGame.StartNewGame()
            

# GetCrossRef()

# Abre un archivo llamado "crossref.txt" que contiene referencias cruzadas entre identificadores de fichas
# y nombres de fichas.

# Lee el archivo, asigna nombres de fichas a identificadores y carga imágenes correspondientes.
# Realiza ajustes en los colores de las imágenes según los colores del laberinto.

def GetCrossRef ():

    f = open(os.path.join(SCRIPT_PATH,"res","crossref.txt"), 'r')


    lineNum = 0
    useLine = False

    for i in f.readlines():
        while len(i)>0 and (i[-1]=='\n' or i[-1]=='\r'): i=i[:-1]
        while len(i)>0 and (i[0]=='\n' or i[0]=='\r'): i=i[1:]
        str_splitBySpace = i.split(' ')
        
        j = str_splitBySpace[0]
            
        if (j == "'" or j == "" or j == "#"):
            useLine = False
        else:
            useLine = True
        
        if useLine == True:
            tileIDName[ int(str_splitBySpace[0]) ] = str_splitBySpace[1]
            tileID[ str_splitBySpace[1] ] = int(str_splitBySpace[0])
            
            thisID = int(str_splitBySpace[0])
            if not thisID in NO_GIF_TILES:
                tileIDImage[ thisID ] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","tiles",str_splitBySpace[1] + ".gif")).convert()
            else:
                    tileIDImage[ thisID ] = pygame.Surface((16,16))
            
            for y in range(0, 16, 1):
                for x in range(0, 16, 1):
                
                    if tileIDImage[ thisID ].get_at( (x, y) ) == (255, 206, 255, 255):
                        tileIDImage[ thisID ].set_at( (x, y), thisLevel.edgeLightColor )
                        
                    elif tileIDImage[ thisID ].get_at( (x, y) ) == (132, 0, 132, 255):
                        tileIDImage[ thisID ].set_at( (x, y), thisLevel.fillColor ) 
                        
                    elif tileIDImage[ thisID ].get_at( (x, y) ) == (255, 0, 255, 255):
                        # pellet color
                        tileIDImage[ thisID ].set_at( (x, y), thisLevel.edgeShadowColor )   
                        
                    elif tileIDImage[ thisID ].get_at( (x, y) ) == (128, 0, 128, 255):
                        # pellet color
                        tileIDImage[ thisID ].set_at( (x, y), thisLevel.pelletColor )   
                
        lineNum += 1

# Main Code Block:
# Crea instancias de clases para el jugador, el buscador de caminos, fantasmas, y frutas.
# Inicializa el joystick si está disponible.
# En un bucle principal, maneja diferentes modos del juego (inicio, juego normal, pausas, etc.).
# Verifica la entrada del usuario, mueve elementos del juego, y actualiza la pantalla.
# Se incluyen acciones específicas para diferentes modos de juego, como pausas, colisiones y cambios de nivel.


# Creando el pacman

player = pacman()

# Crear un objeto path_finder.
path = path_finder()

# Crear fantasmas
ghosts = {}
for i in range(0, 6, 1):
    # Recuerda, el fantasma[4] es el fantasma azul y vulnerable.
    ghosts[i] = ghost(i)
    
# Crear una pieza de fruta.
thisFruit = fruit()

tileIDName = {} 
tileID = {} 
tileIDImage = {} 

# crea objetos de juego y nivel y carga el primer nivel
thisGame = game()
thisLevel = level()
thisLevel.LoadLevel( thisGame.GetLevelNum() )

window = pygame.display.set_mode( thisGame.screenSize, pygame.DOUBLEBUF | pygame.HWSURFACE )

# inicializa el joystick
if pygame.joystick.get_count()>0:
  if JS_DEVNUM<pygame.joystick.get_count(): js=pygame.joystick.Joystick(JS_DEVNUM)
  else: js=pygame.joystick.Joystick(0)
  js.init()
else: js=None

while True: 

    CheckIfCloseButton( pygame.event.get() )
    
    if thisGame.mode == 1:
        # juego modo normal
        CheckInputs()
        
        thisGame.modeTimer += 1
        player.Move()
        for i in range(0, 4, 1):
            ghosts[i].Move()
        thisFruit.Move()
            
    elif thisGame.mode == 2:
        # esperando después de ser golpeado por un fantasma
        thisGame.modeTimer += 1
        
        if thisGame.modeTimer == 90:
            thisLevel.Restart()
            
            thisGame.lives -= 1
            if thisGame.lives == -1:
                thisGame.updatehiscores(thisGame.score)
                thisGame.SetMode( 3 )
                thisGame.drawmidgamehiscores()
            else:
                thisGame.SetMode( 4 )
                
    elif thisGame.mode == 3:
        # Juego terminado
        CheckInputs()
            
    elif thisGame.mode == 4:
        # esperando para comenzar
        thisGame.modeTimer += 1
        
        if thisGame.modeTimer == 90:
            thisGame.SetMode( 1 )
            player.velX = player.speed
            
    elif thisGame.mode == 5:
        # breve pausa después de devorar a un fantasma vulnerable
        thisGame.modeTimer += 1
        
        if thisGame.modeTimer == 30:
            thisGame.SetMode( 1 )
            
    elif thisGame.mode == 6:
        # pausa después de comer todos los pellets
        thisGame.modeTimer += 1
        
        if thisGame.modeTimer == 60:
            thisGame.SetMode( 7 )
            oldEdgeLightColor = thisLevel.edgeLightColor
            oldEdgeShadowColor = thisLevel.edgeShadowColor
            oldFillColor = thisLevel.fillColor
            
    elif thisGame.mode == 7:
        # laberinto parpadeante después de completar el nivel
        thisGame.modeTimer += 1
        
        whiteSet = [10, 30, 50, 70]
        normalSet = [20, 40, 60, 80]
        
        if not whiteSet.count(thisGame.modeTimer) == 0:
            # member of white set
            thisLevel.edgeLightColor = (255, 255, 255, 255)
            thisLevel.edgeShadowColor = (255, 255, 255, 255)
            thisLevel.fillColor = (0, 0, 0, 255)
            GetCrossRef()
        elif not normalSet.count(thisGame.modeTimer) == 0:
            thisLevel.edgeLightColor = oldEdgeLightColor
            thisLevel.edgeShadowColor = oldEdgeShadowColor
            thisLevel.fillColor = oldFillColor
            GetCrossRef()
        elif thisGame.modeTimer == 150:
            thisGame.SetMode ( 8 )
            
    elif thisGame.mode == 8:
        # pantalla en blanco antes de cambiar de nivel
        thisGame.modeTimer += 1
        if thisGame.modeTimer == 10:
            thisGame.SetNextLevel()

    thisGame.SmartMoveScreen()
    
    screen.blit(img_Background, (0, 0))
    
    if not thisGame.mode == 8:
        thisLevel.DrawMap()
        
        if thisGame.fruitScoreTimer > 0:
            if thisGame.modeTimer % 2 == 0:
                thisGame.DrawNumber (2500, thisFruit.x - thisGame.screenPixelPos[0] - 16, thisFruit.y - thisGame.screenPixelPos[1] + 4)

        for i in range(0, 4, 1):
            ghosts[i].Draw()
        thisFruit.Draw()
        player.Draw()
        
        if thisGame.mode == 3:
                screen.blit(thisGame.imHiscores,(32,256))
        
    if thisGame.mode == 5:
        thisGame.DrawNumber (thisGame.ghostValue / 2, player.x - thisGame.screenPixelPos[0] - 4, player.y - thisGame.screenPixelPos[1] + 6)
    
    
    
    thisGame.DrawScore()
    
    pygame.display.flip()
    
    clock.tick (60)
