from willow.willow import *
import sys

# variables for experiment, static ones capitalized, counters and payoffs lower case
NUM_GAMES = 3
NUM_PLAYERS = 2
NUM_ITERS = 3
NODES_PER_GAME = 5
game_iters = -1
little_payoff = 1
big_payoff = 2

# variable to determine the session number for the monitor based on the number of total players in the experiment
MON_SESSION = NUM_GAMES*NUM_PLAYERS


# array that contains node position for all games
game_node = []

# array that contains flag for whether players have clicked next game buttom    
clicked_next = []

# a map of arrays that assign each player a game, and position in that game
role_map = [
    [0,0],
    [0,1],
    [1,0],
    [1,1],
    [2,0],
    [2,1],
     
  ]

# creates an array that will monitor whether each game has finished by using an boolean item representing each game in the array
game_over = []



# calculates the big payoff based on the node in the game
def get_big_payoff(node):
    return big_payoff**(node+1)

# calculates the little payoff based on the node in the game
def get_little_payoff(node):
    return little_payoff*node

# maping function, handed the session number and returns an array with game and position based on the assignments in role_map 
def my_role(session_id):
    return role_map[session_id]
    
# returns an array containing all player sessions, utelized to communicate with each player in the game
def all_players():
    return range(NUM_GAMES*NUM_PLAYERS)

# function that is handed a position and returns all other positions in the game, in order to communicate with all other players after a decision has been made
def other_sessions_in_my_game(my_session):

    # create look up table that returns who the other player in the game is CHEATING
    return {
        '0' : [1],
        '1' : [0],
        '2' : [3],
        '3' : [2],
        '4' : [5],
        '5' : [4],
        
    # converts my session to a string, and use the dictionary above to look up the other player in the game
    }[str(my_session)]


# function that checks to see which sessions have clicked next game button,
# if every next button has been clicked, puts a unique dictionary for each player that signals the start of the next game
def check_game(session_id):
    global clicked_next
    
    # clicked_next is our array that contains Boolean values on whether the given session has ended the game (as reported by player one). 
    clicked_next[session_id] = True

    #create boolean variable all_clicked and set it to True
    all_clicked = True

    # walks through the list clicked_next containing the boolean values on whether each game has finished
    for p in clicked_next:
        # if any of the items in the list are not True
        if not p:
            # sets the variable all_clicked to False
            all_clicked = False

    # when the variable all_click is True        
    if all_clicked:
        # walk through a loop of all the players, and put a dictionary on the board with each of their session number to notify that the game has started
        for p in all_players():
            put({"start_game": p})


    
# function that will control the monitor session
def do_mon():
    
  global game_iters
  global game_node
  global game_over
  global clicked_next
    
  # adds the monitor HTML page to the browser window
  add(open("mon.html"))
  
  # creates condition that will always be true
  while(True):

      #set up next game here

      new_game = True    
      # tests to see if all items in game_over are true, to start new game
      # for loop that increments through each item in game_over
      for g in game_over:
          # if the specified item g in game_over contains False, set all_done to False
          if not g:
              new_game = False
              
      # If all_done is still true after the for loop, then every item in game_over was true, and all games have ended
      if new_game:
            
          # incrememnt iteration
          game_iters += 1

          # emptying the previous contents in our arrays

          game_node = []
          game_over = []
          clicked_next = []


          # create array from NUM_GAMES using the range function, walk through and reset all game nodes to 0 and each game_over flag to 0
          for i in range(NUM_GAMES):
              game_node.append(0)
              game_over.append(False)
              
          # create array based on total number of players in the experiment
          for i in range(NUM_GAMES*NUM_PLAYERS):
              clicked_next.append(False)

          # read in and set up role map from a file

          # display button for next game
          hide("#controls", all_players())
          sys.stderr.write("Iter Number: " + str(game_iters) + "\n")
          # display the iteration number in the correct span
          let(game_iters, "#iter_number")

          # walk through all the players identified in the all_players function
          for p in all_players():
              # put a dictionary on the board for each that specifies the session number with the key initial state
              put({"init_state": p})
                       
          
              
      # variable that looks for any of the dictionaries put out by the monitor
      clicker = take({'tag': 'click', 'client':6}, {"tag": "game_over"}, {"tag": "session_ready"})
      if clicker["tag"] == "click":
          #if show button is clicked
          if clicker["id"] == "showdebug":
              #display the debug section to all players as specified in the all_players function
              show("#debug", all_players())
          else:          
             #hide the debug section to all players as specified in the all_players function
             hide("#debug", all_players())
      # when a game ends and sends a dictionary, changes the item in game_over list to be true
      elif clicker["tag"] == "game_over":
          game_over[clicker["game"]] = True
          sys.stderr.write("Game " + str(clicker["game"]) + " Has ended")

      # when one of the sessions send a dictionary says that it is ready
      elif clicker["tag"] == "session_ready":                    
          # call the check_game function
          check_game(clicker["session"])

              
      
# function that will be run every time a browser connects to the host  
def session(me):
  global game_node
  global session_ready
  global little_payoff
  global big_payoff
  
  # condition for the monitor session  
  if me == MON_SESSION:
      do_mon()
      
  #adds the subject HTML page to the browser   
  add(open("subject.html"))

  #displays the session number in the specified span
  let(me, "#session_num")

  #hides the debug and controls section from the page
  hide("#debug, #controls")
  
  let("", "#message")

  #creates condition that will always be true so long as the experiement is being run
  while(True):

      
      #set up and assign game and role
      hide("#next_game")
      

      # wait for the start of game signal from mon
      take({"init_state": me})
      show("#next_game")

      # take click from the next game button
      take({"tag":"click", "id": "next", "client": me})
      hide("#next_game")
      let("Please wait for all players", "#message")
      put({"tag": "session_ready", "session": me})

      # now waiting for mon to tell you the game is ready to go
      take({"start_game": me})
      
      
      #read the map to determine game and position

      
      #assigns variable that will hold the array returned from the my_role function
      role_info = my_role(me)
      #assigns variable that will determine which game each session will be involved in
      my_game = role_info[0]
      #assigns variable that will determine which position in the game each session will be
      my_position = role_info[1]



      #dispays which game the player has been assigned to in a span
      let(str(my_game),"#game_number")
      #dispays which position the player has been assigned to in a span
      let(str(my_position), "#player_number")


      #game loop
      #condition that will be True while the node counter is less than the defined number of nodes in a game
      while(game_node[my_game] < NODES_PER_GAME):

          # esentially says, look if dictionary is there, take it, get out of the while loop - if it is not there, continue on your way
          # grab is a function like take, but only checks for a dictionary once and does not wait if it is not on the board. If there is no matching dictionary it returns a value "None"
          if grab({"tag":"end_of_game", "session": me}) != None:
              sys.stderr.write("Inner Poop")
              break #get the fuck out of the game loop
          

          
          let(str(game_node[my_game]), "#node_number")
          # if the remainder of the current node by the total number of players in the game is equal to a players assigned position   
          sys.stderr.write("Node" + str(game_node[my_game]) + "\n")
          sys.stderr.write("My Pos" + str(my_position) + "\n")

          if (game_node[my_game]%NUM_PLAYERS) == my_position:
              # display the buttons for making a selection
              show("#controls")
              let("If you chose down, you will earn %d and the other player will earn %d. <br> If you chose across, you will pass to the next player"
                  %(get_big_payoff(game_node[my_game]), get_little_payoff(game_node[my_game])), "#message")
              
              
              # collect the click from the player
              choice = take({'tag': 'click', 'client': me})

              # if statement for whether the click was across goes here

              if choice["id"] == "across":
              
                  hide("#controls")
                  # increment the node counter
                  game_node[my_game] += 1
                  

              # else statement for if player clicks down
              # create for loop that will put a unique dictionary out for each player in the list other_sessions_in_my_game

              elif choice["id"] == "down":


                  for p in other_sessions_in_my_game(me):
                      # put a dictionary out for every other player as specified by the role_map
                      put({"tag":"end_of_game", "session": p})
                      
                  # put out a unique dictionary for me as well
                  put({"tag":"end_of_game", "session": me})

              else:
                  sys.stderr.write("WHY NO WORK?" + " " + str(me) + " " + choice["id"] + "\n")

              
              # Other Sessions in my game is now 
              # test_array = other_sessions_in_my_game(me)

              # put({"tag" : "game_step", "session" : test_array})


              #sys.stderr.write("This is returning: " + str(test_array))
                               
              #for p in test_array.iteritems():
                  #sys.stderr.write("This Array Returns" + str(test_array[p]) + "\n")
                      
              for p in other_sessions_in_my_game(me):

                      # puts out a unique dictionary specified by the game and position 
                      put({"tag": "game_step", "session": p})
                      sys.stderr.write("P is" + str(p) + "\n")  

            
                  
          # condition for if it is not a players turn    
          else:
              # notify them with a waiting message
              let("NOT YO TURN", "#message")
              # wait for a dictionary with a bogus tag to appear, which will keep the function waiting forever
              take({"tag": "game_step", "session": me})

      # fall out of the while loop that continues for the duration of a single game

      hide("#controls")
      
      # person that will notify the monitor session that the game is over, arbitrarily position 0
      if my_position == 0:

          # position one player will write out file here
          
          # look at game node, determine what the payoffs were, and write them out
          # will need if statement for if we reached the last node

          # put a dictionary that signals the game is over, and identifies which game has ended to mon
          put({"tag": "game_over", "game": my_game})


          
      # send message to 
      let("Game Over, please wait.<br> You earned %d" %(get_big_payoff(game_node[my_game])), "#message")

      
# run the session function so people can connect
run(session, 8000)
