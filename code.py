playerId=""
feedbackSended=False

def sql(statements):
    cur.execute(statements)
    return cur.fetchall()


def sql2(statements):
    cur.execute(statements)
    array=cur.fetchall()
    return [row[0] for row in array]


def drop(item):
    global playerId
    if item=="drop":
        textText.set("What I want to drop ?")
    else:
        slots={0:"bigslot",1:"smallslot1",2:"smallslot2"} 
        for x in range (3):
            var=sql2("select name from items where id =(select "+slots[x]+" from player where id="+playerId+")")
            if item!=str(*var):
                del slots[x]
        if len(slots):
            cur.execute("update player set "+str(*slots.values())+"='0' where id="+playerId)
            cur.execute("update items set roomname=(select roomname from player where id="+playerId+") where name ='"+str(*var)+"'")
        else:
            textText.set("I don't have it")


def get (items):

	global playerId
	result = sql("SELECT items.Type,\
	 player.BigSlot, player.SmallSlot1, player.SmallSlot2, items.Id FROM items, player\
	 WHERE player.RoomName = items.RoomName AND items.GetItem = 1 AND \
	 items.Name = '" + str(items) + "' AND player.Id='"+str(playerId)+"'")

	#If there are no items
	if result == []:
		textText.set("I can't see the " + str(items) + " anywhere.")

	#If the item is big
	elif result[0][0] == 1:
		#Checks item slot
		if result[0][1] == 0:
			cur.execute("UPDATE items SET items.RoomName = NULL WHERE items.Name = '" + str(items) + "'")
			cur.execute("UPDATE player SET player.BigSlot = '" + str(result[0][4]) + "'")
		else:
			textText.set("I can't take that item right now")

	#If the item is small
	elif result[0][0] == 0:
		#Checks item slots
		if result[0][2] == 0:
			cur.execute("UPDATE items SET items.RoomName = NULL WHERE items.Name = '" + str(items) + "'")
			cur.execute("UPDATE player SET player.SmallSlot1 = '" + str(result[0][4]) + "'")
		elif result[0][3] == 0:
			cur.execute("UPDATE items SET items.RoomName = NULL WHERE items.Name = '" + str(items) + "'")
			cur.execute("UPDATE player SET player.SmallSlot2 = '" + str(result[0][4]) + "'")
		elif result [0][1] == 0:
			cur.execute("UPDATE items SET items.RoomName = NULL WHERE items.Name = '" + str(items) + "'")
			cur.execute("UPDATE player SET player.BigSlot = '" + str(result[0][4]) + "'")
		else:
			textText.set("I can't hold more items.")

	#If every slot is full
	else:
		textText.set("I can't hold more items. #THIS SHOULDN'T BE VISIBLE#")

#Handle using items
def use (target):

    sql = "SELECT items.Id, items.Name, items.UseItem, items.RoomName, player.RoomName, items.TextId, items.UseFunction\
            FROM items, player WHERE items.RoomName = player.RoomName AND player.Id = '"+playerId+"' \
            OR (player.BigSlot = items.Id OR player.SmallSlot1 = items.Id OR player.SmallSlot2 = items.Id) And player.Id = '"+playerId+"';"
	
    #execute the query
    cur.execute(sql)
    #get the query result
    result = cur.fetchall()
    #initialize new tuple
    itemTuple = ()

    for item in result:
        if target in item:
            itemTuple = item

    #found target item    
    if len(itemTuple) > 0:
        #"item has a use
        if str(itemTuple[2]) != "None":
            #using in the right room
            if (itemTuple[2] == itemTuple[4]):
                #Get item use function attributes and split after ,
                func = str(itemTuple[6]).split(",")
                if "sql" in func:
                    #handle attributes containing sql functions using the second element
                    sql = str(func[1])
                    cur.execute(sql)
                    #Get item usage text
                    texts(itemTuple[5], "use")
                else:
                    #Send use info for unqiue situations
                    texts(itemTuple[5], "use")
            elif itemTuple[2] == "ALL":
                #Get item usage text
                texts(itemTuple[5], "use")
            else:
                if str(itemTuple[2]) == "None":
                    #item has no use
                    textText.set("I don't think I can use this at all!")
                else:
                    #using item in the wrong room
                    textText.set("I can't use that here!")
        else:
            #item has no use
            textText.set("I don't think I can use this at all!")
    else:
        #player doesn't have access to the target item
        textText.set("I can't find that item!")


def funcChoose(event):
    inputValue=textBox.get("1.0","end-1c")
    textBox.delete('1.0', END)
    inputValue=inputValue.replace("\n","")
    #inputValue=inputValue.lower()
    index=0
    inputValue=inputValue.split(" ")
    if inputValue.count("from"):
        index = inputValue.index("from")
    if inputValue.count("wait"):
        counter+=1
    if inputValue.count("get") or inputValue.count("take"):
        get(inputValue[len(inputValue)-index-1])
    elif inputValue.count("use"):
        use(inputValue[len(inputValue)-index-1])
    elif inputValue.count("examine") or inputValue.count("look"):
        texts(inputValue[len(inputValue)-index-1], "examine")        
    elif inputValue.count("drop"):
        drop(inputValue[-1],1)
    elif inputValue.count("throw"):
        drop(inputValue[-1],0)
    elif inputValue.count("exit") or inputValue.count("quit") or inputValue.count("escape"):
        window.destroy()
    else:
        textText.set("What shall I do ?")
    showItems()



def showItems():
    sqlAnswer=[]
    sqlAnswer.append(sql2("select items.Name from items, player where smallslot1=items.id and player.Id="+playerId))
    sqlAnswer.append(sql2("select items.Name from items, player where smallslot2=items.id and player.Id="+playerId))
    sqlAnswer.append(sql2("select items.Name from items, player where bigslot=items.id and player.Id="+playerId))
    inventoryText.set("INVENTORY:\nLeft pocket\t: "+str(*sqlAnswer[0])+"\nRight pocket\t: "+str(*sqlAnswer[1])+"\nIn the hands\t: "+str(*sqlAnswer[2]))


#lower()


def movement(direction):

    var=sql2("select roomname from player where id="+playerId)
    try:
        if direction!="":
            if int(*sql2("select counter from rooms where name=(select "+direction+" from rooms where name=\""+str(*var)+"\")"))==-1:
                textText.set("It's locked!")
            else:
                cur.execute("update player SET RoomName=(select "+direction+" from rooms where name=\""+str(*var)+"\") where id="+playerId)
                textText.set("")
                var=sql2("select roomname from player where id="+playerId)
                #print(var[0], var[0]=="A1", var[0]=="D2",var[0]== "F3")
                if var[0]=="A1" or var[0]=="D2" or var[0]== "F3":
                    #save()
                    #textText.set("I feel safe here")
                hiddenText.set("")
                cur.execute("update player set hidden=0 where id="+playerId)
                cur.execute("update rooms set first_time='1' where name like'"+str(*var)[:1]+"%'")
        positionText.set(str(*sql2("select description from rooms where name=(select roomname from player where id="+playerId+")")))
        directions=["west","north","east","south"]
        for x in range (4):
            var2=sql2("select description from rooms where name=(select "+directions[x]+" from rooms where name=(select roomname from player where id="+playerId+"))")
            if len(var2):
                if int(*sql2("select first_time from rooms where name=(select "+directions[x]+" from rooms where name=\""+str(*var)+"\")")):
                    text=str(*var2)
                else:
                    text="****"
            else:
                text=""

            if x==0:
                westText.set(text)
            elif x==1:
                northText.set(text)
            elif x==2:
                eastText.set(text)
            else:
                southText.set(text)
        texts(str(*var), "enter")

    except:{}


#Prints out the current rooms description or if target if given then prints out targets description
def texts(target, action):
    #if target is not 'Room' gets target items texts
    if target not in ["examine", "look"]:
        #Get item.Id to query the texts
        sql = "SELECT items.TextId FROM items, player WHERE items.Name LIKE '" + target + "%' AND (items.RoomName = player.RoomName OR items.RoomName = NULL);"
        cur.execute(sql)
        newTarget = cur.fetchall()
        #if a item id was found set it as target
        if newTarget != []:
            target = str(*newTarget[0])
        #check if item is furniture and if so get room suffix
        sql = "SELECT RoomName FROM items WHERE TextId = '" + target + "' AND Type = 1;"
        cur.execute(sql)
        newAction = cur.fetchall()
        #if item is furniture and if so add room suffix
        if newAction != [] and action == "examine":
            if str(newAction[0][0]) != "None":
               action = action + newAction[0][0]      
    else:
        #Target is not an item so the room examine will be printed
        sql = "SELECT RoomName FROM player where Id='"+playerId+"';"
        cur.execute(sql)
        roomName = cur.fetchall()
        target = str(roomName[0][0])
    if target != "":
        #sql query to get text with id and subId
        sql = "SELECT Text, BigText FROM texts WHERE id = '" + target + "' AND SubId = '" + action + "';"
        cur.execute(sql)
        textPrint = cur.fetchall()
        #print appropriate text or bigText if one is found
        if textPrint != []:
            if str(textPrint[0][0]) != "None":
                textText.set(textPrint[0][0])
            else:
                textText.set(textPrint[0][1])
        else:
            allItems=sql2("select name from items")
            if target in allItems:
                textText.set("A usual "+target+". Nothing special.")
            else:
                textText.set("Look what ?")    
    else:
        #read text below
        textText.set("Something went wrong")
        
def hidden():
    roomItems=sql2("select name from items where roomname=(select roomname from player where id="+playerId+")")
    if "Bed" in roomItems or "Cupboard" in roomItems or "Desk" in roomItems or "Caretaker's Table" in roomItems:
        if int(*sql2("select hidden from player where id="+playerId)):
            #hiddenBottonColor.configure(background='green')
            hiddenText.set("Unhidden")
            cur.execute("update player set hidden=0 where id="+playerId)
            #hiddenText.Update()
        else:
            #hiddenBottonColor.configure(background='red')
            hiddenText.set("Hidden")
            cur.execute("update player set hidden=1 where id="+playerId)
            #hiddenText.Update()
    else:
        textText.set("I don't see any hidden place.")
        
def save():
    global playerId
    toDB=""
    array = sql("select Id, RoomName, Bigslot,smallSlot1,smallslot2 from player where Id="+playerId)
    array += "///"
    array += sql("select Id, Roomname from items")
    array += "///"
    array += sql("select Name, First_time from rooms")
    for x in range (len(array)):
        toDB+=str(array[x])
    cur.execute("rollback")
    cur.execute("update player set saveOptions=\""+toDB+"\" where id="+playerId)
    cur.execute("commit")
    load()

    

def load():
    global playerId
    fromDB=str(sql2("select saveOptions from player where id="+playerId))
    data = fromDB.split("///")
    data[0] = data[0].replace(")", "")

    for i in range(3):
        data[i] = data[i].replace("(", "")
        data[i] = data[i].replace("'", "")
        data[i] = data[i].replace(" ", "")
    data[0] = data[0].split(",")
    data[1] = data[1].split(")")        

    for i in range(len(data[1])):
        data[1][i] = data[1][i].split(",")

    data[2] = data[2].split(")")
    
    for i in range(len(data[2])):
        data[2][i] = data[2][i].split(",")
    cur.execute("UPDATE player SET RoomName = '"+str(data[0][1])+"', \
        BigSlot = '"+str(data[0][2])+"', \
        SmallSlot1 = '"+str(data[0][3])+"', \
        SmallSlot2 = '"+str(data[0][4])+"' \
        WHERE Id = '"+playerId+"'")
   
    for i in range(len(data[1])-1):
        cur.execute("UPDATE items SET RoomName = '"+ str(data[1][i][1])+"' WHERE Id='"+str(data[1][i][0])+"'")

    for i in range(len(data[2])-1):
        cur.execute("UPDATE rooms SET First_time = '"+ str(data[2][i][1])+"' WHERE Name = '"+ str(data[2][i][0])+"'")


def mainStart():
    movement("")
    showItems()



##def startMenu():
##    def menuStartButton():
##        menuStart("<Return>")
##    def feedback():
##        def sendFeedback():
##            global feedbackSended
##            feedbacklogin=feedbackloginInput.get("1.0","end-1c")
##            feedbackpw=feedbackpwInput.get("1.0","end-1c")
##            if sql2("select id from player where savename='"+feedbacklogin+"' and savepass='"+feedbackpw+"'")==[]:
##                feedbackLabelText.set("Wrong login or password!\nPlease try again!")
##            else:
##                sql="update player set feedback='"+feedbackText.get("1.0","end-1c")+"\n"+feedbackpostInput.get("1.0","end-1c")+"\
##                    ' where savename='"+feedbacklogin+"' and savepass='"+feedbackpw+"'"
##                cur.execute(sql)
##                cur.execute("commit")
##                feedbackSended=True
##                feedbackWindow.destroy()
##                startMenu()
##        def feedbackBackButton():
##            global feedbackSended
##            feedbackWindow.destroy()
##            feedbackSended=False
##            startMenu()
##            
##        startWindow.destroy()
##        feedbackWindow=Tk()
##        feedbackWindow.title("False Awakening/Feedback")
##        frame=Frame(height=455, width=460,bg="azure").grid(rowspan=40,columnspan=40)
##        feedbackLabelText = StringVar()
##        feedbackLabel=Label(height=3, width=30, textvariable=feedbackLabelText,bg="azure",anchor='n', font=("Times", 16))
##        feedbackLabel.grid(row=0,column=0,columnspan=5)
##        feedbackLabelText.set("Your feedback is realy important for us!\nThank you!")        
##        feedbackText=Text(height=15, width=45)
##        feedbackText.grid(row=1,column=0,columnspan=5)        
##        feedbackpostLabel=Label(bg="azure",text="Email(optional)").grid(row=2)
##        feedbackpostInput=Text(height=1,width=40,font=("Times", 12))
##        feedbackpostInput.grid(row=2,column=1,columnspan=4)
##        feedbackText.focus()
##        feedbacklogin=Label(text="Login",bg="azure", font=("Times", 16)).grid(row=3,column=0)
##        feedbackloginInput=Text(height=1,width=10, font=("Times", 16))
##        feedbackloginInput.grid(row=3, column=1)
##        feedbackpw=Label(text="Password",bg="azure", font=("Times", 12)).grid(row=3,column=2)
##        feedbackpwInput=Text(height=1,width=10, font=("Times", 16))
##        feedbackpwInput.grid(row=3, column=3)
##        backButton=Button(text="Back",height=2, width=5, command=feedbackBackButton, font=("Times", 20)).grid(row=4,column=0)
##        sendButton=Button(text="Send feedback!",height=2, width=23, command=sendFeedback, font=("Times", 20)).grid(row=4,column=1,columnspan=4)
##        
##        feedbackWindow.mainloop()
##        
##    def menuStart(event):
##        global playerId
##        loginValue=loginInput.get("1.0","end-1c")
##        loginInput.delete('1.0', END)
##        loginValue=loginValue.replace("\n","")
##        pwValue=pwInput.get("1.0","end-1c")
##        pwInput.delete('1.0', END)
##        pwValue=pwValue.replace("\n","")
##        if newPlayerCheck.get():
##            if loginValue=="" or pwValue=="":
##                startText.set("Empty fields!\nTry again!")
##            else:
##                try:
##                    cur.execute("insert into player (savename,savepass) values ('"+loginValue+"','"+pwValue+"')")
##                    answer=sql2("select max(id) from player")
##                    playerId=str(*answer)
##                    startWindow.destroy()
##                    cur.execute("commit")            
##                except:
##                    startText.set("Input login in use.\nPlease try another login!")
##
##        else:
##            answer=sql2("select id from player where savename='"+loginValue+"' and savepass='"+pwValue+"'")
##            if answer==[]:
##                startText.set("Wrong login or password!\nPlease try again!")
##                return
##            playerId=str(*answer)
##            startWindow.destroy()
##            load()
##
##    global feedbackSended
##    startWindow=Tk()
##    startWindow.title("False Awakening/Start Menu")
##    frame=Frame(height=270, width=485,bg="azure").grid(rowspan=40,columnspan=40)
##
##
##    startText = StringVar()
##    text=Label(height=8, width=40, textvariable=startText,anchor='n',bg="azure", font=("Times", 16)).grid(row=0,column=0,columnspan=5)
##    if feedbackSended:
##        startText.set("Feedback sended\nThank you very much!\n\n\n\n\nNow you can log in to game")
##    else:
##        startText.set("Welcome to \"False Awakening\"\n\nby Sergey Pritchin,\nAku Korhonen \nand Nico Behnen!\n\n\nPlease log in or sing up")
##
##    login=Label(text="Login",bg="azure", font=("Times", 12)).grid(row=1,column=0)
##    loginInput=Text(height=1, width=10, font=("Times", 16))
##    loginInput.grid(row=1, column=1)
##    loginInput.bind("<Return>", menuStart)
##    pw=Label(text="Password",bg="azure", font=("Times", 12)).grid(row=1,column=2)
##    pwInput=Text(height=1, width=10, font=("Times", 16))
##    pwInput.grid(row=1, column=3)
##    pwInput.bind("<Return>", menuStart)
##    loginButton=Button(text="Log in", font=("Times", 12),command=menuStartButton).grid(row=1,column=4)
##
##    newPlayerCheck=IntVar()
##    newPlayer=Checkbutton(text="I am a new player!",bg="azure",variable=newPlayerCheck).grid(row=3,column=0,columnspan=3)
##    emptyLabel=Label(height=1, width=40,bg="azure").grid(row=2,columnspan=4)
##    feedback=Button(text="Left feedback to developers", command=feedback).grid(row=3,column=3)
##
##    startWindow.mainloop()
playerId="33"

                    
cur=db.cursor()
#startMenu()


window = Tk()
window.title("False Awakening")

northText = StringVar()
westText = StringVar()
positionText = StringVar()
eastText = StringVar()
southText = StringVar()
inventoryText = StringVar()
textText = StringVar()
hiddenText=StringVar()

text=Label(height=15, width=60, textvariable=textText,anchor='n',justify=LEFT,wraplength=700 ,bg="azure", font=("Times", 16)).grid(row=0, column=0,rowspan=6)


    
northBotton=Button(height=2, width=20, textvariable=northText,command=lambda:movement("north")).grid(row=0,column=2)
westBotton=Button(height=2, width=20, textvariable=westText,command=lambda:movement("west")).grid(row=1,column=1)
position=Label(height=2, width=20, textvariable=positionText).grid(row=1,column=2)
eastBotton=Button(height=2, width=20, textvariable=eastText,command=lambda:movement("east")).grid(row=1,column=3)
southBotton=Button(height=2, width=20, textvariable=southText,command=lambda:movement("south")).grid(row=2,column=2)

hiddenBotton=Button(height=3, width=40, textvariable=hiddenText,command=hidden).grid(row=3,column=1, columnspan=3)

inventoryLabel=Label(height=7, width=35, textvariable=inventoryText, justify=LEFT,bg="light goldenrod", font=("Times", 16)).grid(row=5, column=1, rowspan=10, columnspan=10)



textBox=Text(height=1, width=65, font=("Times", 16))
textBox.grid(row=11, column=0)
textBox.bind("<Return>", funcChoose)

mainStart()

window.mainloop()
