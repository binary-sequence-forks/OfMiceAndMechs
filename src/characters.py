import src.items as items
import src.quests

characters = None
calculatePath = None
roomsOnMap = None

class Character():
    def __init__(self,display="＠",xPosition=0,yPosition=0,quests=[],automated=True,name="Person"):
        self.display = display
        self.xPosition = xPosition
        self.yPosition = yPosition
        self.automated = automated
        self.quests = []
        self.name = name
        self.inventory = []
        self.watched = False
        self.listeners = []
        self.room = None
        self.terrain = None
        self.path = []
        self.subordinates = []
        self.reputation = 0

        self.gotBasicSchooling = False
        self.gotMovementSchooling = False
        self.gotInteractionSchooling = False
        self.gotExamineSchooling = False

        self.satiation = 1000
        self.dead = False
        self.questsToDelegate = []

        #TODO: this approach is fail, but works for now. There has to be a better way
        self.basicChatOptions = []

        self.assignQuest(src.quests.SurviveQuest())
        
        for quest in quests:
            self.assignQuest(quest)

        self.inventory.append(items.GooFlask())

    def getChatOptions(self,partner):
        chatOptions = self.basicChatOptions[:]
        if not self in partner.subordinates:
            chatOptions.append(interaction.RecruitChat)
            pass
        
        return chatOptions

    def getState(self):
        return { "gotBasicSchooling": self.gotBasicSchooling,
                 "gotMovementSchooling": self.gotMovementSchooling,
                 "gotInteractionSchooling": self.gotInteractionSchooling,
                 "gotExamineSchooling": self.gotExamineSchooling,
               }

    def setState(self,state):
        self.gotBasicSchooling = state["gotBasicSchooling"]
        self.gotMovementSchooling = state["gotMovementSchooling"]
        self.gotInteractionSchooling = state["gotInteractionSchooling"]
        self.gotExamineSchooling = state["gotExamineSchooling"]

    def getQuest(self):
        if self.room and self.room.quests:
            return self.room.quests.pop()
        else:
            return None

    def startNextQuest(self):
        if len(self.quests):
            self.quests[0].recalculate()
            try:
                self.setPathToQuest(self.quests[0])
            except:
                pass

    def getDetailedInfo(self):
        return "\nname: "+str(self.name)+"\nroom: "+str(self.room)+"\ncoord: "+str(self.xPosition)+" "+str(self.yPosition)+"\nsubs: "+str(self.subordinates)+"\nsat: "+str(self.satiation)+"\nreputation: "+str(self.reputation)

    def assignQuest(self,quest,active=False):
            if active:
                self.quests.insert(0,quest)
            else:
                self.quests.append(quest)
            quest.assignToCharacter(self)
            quest.activate()
            if (active or len(self.quests) == 1):
                try:
                    if self.quests[0] == quest:
                        self.setPathToQuest(quest)
                except:
                    pass

    def setPathToQuest(self,quest):
        if hasattr(quest,"dstX") and hasattr(quest,"dstY"):
            if self.room:
                self.path = self.room.calculatePath(self.xPosition,self.yPosition,quest.dstX,quest.dstY,self.room.walkingPath)
            elif self.terrain:
                self.path = self.terrain.findPath((self.xPosition,self.yPosition),(quest.dstX,quest.dstY))
            else:
                debugMessages.append("this should not happen, character tried to go sowhere but is nowhere")
                self.path = []
        else:
            self.path = []

    def addToInventory(self,item):
        self.inventory.append(item)

    def applysolver(self,solver):
        solver(self)

    def die(self):
        if self.room:
            room = self.room
            room.removeCharacter(self)
            corpse = items.Corpse(self.xPosition,self.yPosition)
            room.addItems([corpse])
        elif self.terrain:
            terrain = self.terrain
            terrain.removeCharacter(self)
            corpse = items.Corpse(self.xPosition,self.yPosition)
            terrain.addItems([corpse])
        else:
            messages.append("this chould not happen, charcter died without beeing somewhere")

        self.dead = True
        self.path = []
        self.changed()

    def walkPath(self):
        if self.dead:
            return

        if not self.path:
            self.setPathToQuest(self.quests[0])

        currentPosition = (self.xPosition,self.yPosition)
        if self.path and not self.path == [currentPosition]:
            nextPosition = self.path[0]

            item = None
            if self.room:
                if nextPosition[0] < currentPosition[0]:
                    item = self.room.moveCharacterWest(self)
                elif nextPosition[0] > currentPosition[0]:
                    item = self.room.moveCharacterEast(self)
                elif nextPosition[1] < currentPosition[1]:
                    item = self.room.moveCharacterNorth(self)
                elif nextPosition[1] > currentPosition[1]:
                    item = self.room.moveCharacterSouth(self)

            else:
                for room in self.terrain.rooms:
                    # north
                    if room.yPosition*15+room.offsetY+room.sizeY == nextPosition[1]+1:
                        if room.xPosition*15+room.offsetX < self.xPosition and room.xPosition*15+room.offsetX+room.sizeX > self.xPosition:
                            localisedEntry = (self.xPosition%15-room.offsetX,nextPosition[1]%15-room.offsetY)
                            if localisedEntry in room.walkingAccess:
                                if localisedEntry in room.itemByCoordinates:
                                    for listItem in room.itemByCoordinates[localisedEntry]:
                                        if not listItem.walkable:
                                            item = listItem
                                            break
                                if item:
                                    break
                                else:
                                    room.addCharacter(self,localisedEntry[0],localisedEntry[1])
                                    self.terrain.characters.remove(self)
                                    self.terrain = None
                                    self.changed()
                                    break
                            else:
                                messages.append("you cannot move there (N)")
                                break
                    # south
                    if room.yPosition*15+room.offsetY == nextPosition[1]:
                        if room.xPosition*15+room.offsetX < self.xPosition and room.xPosition*15+room.offsetX+room.sizeX > self.xPosition:
                            localisedEntry = ((self.xPosition-room.offsetX)%15,((nextPosition[1]-room.offsetY)%15))
                            if localisedEntry in room.walkingAccess:
                                if localisedEntry in room.itemByCoordinates:
                                    for listItem in room.itemByCoordinates[localisedEntry]:
                                        if not listItem.walkable:
                                            item = listItem
                                            break
                                if item:
                                    break
                                else:
                                    room.addCharacter(self,localisedEntry[0],localisedEntry[1])
                                    self.terrain.characters.remove(self)
                                    self.terrain = None
                                    self.changed()
                                    break
                            else:
                                messages.append("you cannot move there (S)")
                                break
                    # east
                    if room.xPosition*15+room.offsetX+room.sizeX == nextPosition[0]+1:
                        if room.yPosition*15+room.offsetY < self.yPosition and room.yPosition*15+room.offsetY+room.sizeY > self.yPosition:
                            localisedEntry = ((nextPosition[0]-room.offsetX)%15,(self.yPosition-room.offsetY)%15)
                            if localisedEntry in room.walkingAccess:
                                if localisedEntry in room.itemByCoordinates:
                                    for listItem in room.itemByCoordinates[localisedEntry]:
                                        if not listItem.walkable:
                                            item = listItem
                                            break
                                if item:
                                    break
                                else:
                                    room.addCharacter(self,localisedEntry[0],localisedEntry[1])
                                    self.terrain.characters.remove(self)
                                    self.terrain = None
                                    self.changed()
                                    break
                            else:
                                messages.append("you cannot move there (E)")
                    # west
                    if room.xPosition*15+room.offsetX == nextPosition[0]:
                        if room.yPosition*15+room.offsetY < self.yPosition and room.yPosition*15+room.offsetY+room.sizeY > self.yPosition:
                            localisedEntry = ((nextPosition[0]-room.offsetX)%15,(self.yPosition-room.offsetY)%15)
                            if localisedEntry in room.walkingAccess:
                                if localisedEntry in room.itemByCoordinates:
                                    for listItem in room.itemByCoordinates[localisedEntry]:
                                        if not listItem.walkable:
                                            item = listItem
                                            break
                                if item:
                                    break
                                else:
                                    room.addCharacter(self,localisedEntry[0],localisedEntry[1])
                                    self.terrain.characters.remove(self)
                                    self.terrain = None
                                    self.changed()
                                    break
                            else:
                                messages.append("you cannot move there (W)")
                                break
                else:
                    self.xPosition = nextPosition[0]
                    self.yPosition = nextPosition[1]
                    self.changed()
            
            if item:
                if isinstance(item,items.Door):
                    item.apply(self)
                return False
            else:
                if (self.xPosition == nextPosition[0] and self.yPosition == nextPosition[1]):
                    self.path = self.path[1:]
            return False
        else:
            return True

    def drop(self,item):
        self.inventory.remove(item)
        item.xPosition = self.xPosition
        item.yPosition = self.yPosition
        if self.room:
            self.room.addItems([item])
        else:
            self.terrain.addItems([item])
        item.changed()
        self.changed()

    def advance(self):
        self.satiation -= 1
        if self.satiation < 0:
            self.die()
            return

        if self.automated:
            if len(self.quests):
                self.applysolver(self.quests[0].solver)
                self.changed()


    def addListener(self,listenFunction):
        if not listenFunction in self.listeners:
            self.listeners.append(listenFunction)

    def delListener(self,listenFunction):
        if listenFunction in self.listeners:
            self.listeners.remove(listenFunction)

    def changed(self):
        for listenFunction in self.listeners:
            listenFunction()

class Mouse(Character):
    def __init__(self,display="🝆 ",xPosition=0,yPosition=0,quests=[],automated=True,name="Mouse"):
        super().__init__(display, xPosition, yPosition, quests, automated, name)
