import random
import pickle


class Player():
    """
    Players have all the below attributes.
    """
    def __init__(self):
        self.jail_card = 0
        self.currency = 500
        self.land = []
        self.location = 1


class Terminopoly():
    """
    This class has all the attributes of the game board and takes
    the players as arguments so it can update their attributes as
    the game progresses.
    """

    def __init__(self, player_one, player_two):
        self.player_one = player_one
        self.player_two = player_two
        # Players get added to the jail list if they go to jail. It is checked at the
        # beginning of their turn, and they have to keep playing the jail sequence
        # for as long as they remain inside.
        self.jail = []
        self.land_stats = {
                            # These are code representations of the property cards.
                            "Python Hotel":{"price":800, "rent":350},
                            "OOP-sy B&B":{"price":650, "rent":300},
                            "CSS Heights":{"price":500, "rent":250},
                            "JS Inn":{"price":400, "rent":200},
                            "Memory Space":{"price":350, "rent":180},
                            "Cache de Cookie":{"price":300, "rent":150},
                            "RAM House":{"price":280, "rent":125},
                            "ROM-ance Inn":{"price":250, "rent":100}
                            }
        self.save_status = {
                            "last to save":0, # Represents the last player who saved (1 or 2).
                            "just loaded":False, # Converts to true if you load a game.
                            }
        self.just_loaded = False
        # This variable represents the last player who saved the game by an integer.
        self.last_save = 0
        # Whenever a player pays rent, the amount gets added to the below deposit.
        # When the next player's turn starts, they add the amount to their funds.
        self.rent_box = 0
        # This list takes the names of any land that has been sold.
        self.sold_land = []


    def chance_draw(self, player, chance_card):
        """
        Runs when the player arrives at a chance location.
        chance_card is always passed in as a random integer between
        1 and 10.
        """
        print(f"The chance card says:")
        if chance_card == 1:
            print("You advance to 'GO' position but the president steals your bonus.")
            player.location = 1
        elif chance_card == 2:
            print("Move back 2 places.")
            player.location -= 2
            self.location_event(player)
        elif chance_card == 3:
            print("Go directly to Jail.")
            player.location = 5
            self.jail.append(player)
            self.jail_sequence(player, 3)
        elif chance_card == 4:
            print("You pay tax of WTC200.")
            player.currency -= 200
            print(f"You now have WTC{player.currency}")
        elif chance_card == 5:
            print("Go to Python Hotel.")
            player.location = 2
            self.land_event("Python Hotel", player)
        elif chance_card == 6:
            print("Go to ROM-ance Inn.")
            player.location = 16
            self.land_event("ROM-ance Inn", player)
        elif chance_card == 7:
            print("Go to Memory Space.")
            player.location = 10
            self.land_event("Memory Space", player)
        elif chance_card == 8:
            print("Go to CSS Heights.")
            player.location = 7
            self.land_event("CSS Heights", player)
        elif chance_card == 9:
            print("A giant eagle picks you up and drops you on a block.")
            player.location = random.randint(1, 16)
            self.location_event(player)
        elif chance_card == 10:
            print("This card can get you out of jail for free! (You keep it.)")
            player.jail_card += 1


    def comm_chest_draw(self, player, comm_chest_card):
        """
        Runs when the player arrives at a community chest.
        comm_chest_card is always passed in as a random integer
        between 1 and 10.
        """
        print(f"The community card says:")
        if comm_chest_card == 1:
            print("You pay school fees of WTC200.")
            player.currency -= 200
            print(f"You now have WTC{player.currency}.")
        elif comm_chest_card == 2:
            print("You get no fines or credit.")
        elif comm_chest_card == 3:
            print("You get WTC20 for being kind.")
            player.currency += 20
            print(f"Your total money is now WTC{player.currency}.")
        elif comm_chest_card == 4:
            print("You move one place forward.")
            player.location += 1
            self.location_event(player)
        elif comm_chest_card == 5:
            print("Your life insurance matures, collect WTC150.")
            player.currency += 150
            print(f"That gets you a total of WTC{player.currency}.")
        elif comm_chest_card == 6:
            print("Pay the hospital bill of WTC250")
            player.currency -= 250
            print(f"You have WTC{player.currency} left.")
        elif comm_chest_card == 7:
            print("Move one space back.")
            player.location -= 1
            self.location_event(player)
        elif comm_chest_card == 8:
            print("Move to GO spot and earn WTC200.")
            player.location = 1
            player.currency += 200
            print(f"You now have a whopping WTC{player.currency}.")
        elif comm_chest_card == 9:
            print("You just got robbed of WTC200 in town.")
            player.currency -= 200
            print(f"You check your pockets: WTC{player.currency} remaining.")
        elif comm_chest_card == 10:
            print("Bank pays you dividend of WTC150.")
            player.currency += 150
            print(f"You now have a massive WTC{player.currency}.")


    def jail_sequence(self, player, tries_left):
        """
        The player can bail themselves out if they have enough WTC,
        or if they have a jail card. If neither, they get three chances
        to roll six. They have to repeat this every turn until they escape
        (see the turn function in this class for the flow of a turn).
        """
        if player.jail_card >= 1:
            give_jail_card = input("Give jail card pass? Y/N").lower()
            if give_jail_card == "y":
                player.jail_card -= 1
                self.jail.remove(player)
                return
        elif player.currency >= 200:
            pay_bail = input("You have enough money for bail – pay WTC200? (y/n): ").lower()
            if pay_bail == "y":
                player.currency -= 200
                print(f"You walk free. You have WTC{player.currency} left.")
                self.jail.remove(player)
                return

        print("You get three tries to roll six for a prison break.")
        while tries_left != 0:
            input("Press enter to roll.")
            outcome = random.randint(1, 6)
            print(f"You roll {outcome}.")
            if outcome != 6:
                tries_left -= 1
                continue
            else:
                print("You drill a hole to freedom!")
                self.jail.remove(player)
                return
        print("Better luck next turn.")


    def land_event(self, land, player):
        """
        This functions gives a player the option to buy the land they arrive
        at if it's not already sold. If it is sold and not owned by them,
        they have to pay rent. If the player already owns the land, it just
        prints a pleasant message.
        """
        if land not in self.sold_land and land not in player.land:
            land_price = self.land_stats[land]["price"]
            if player.currency >= land_price:
                choice = input(f"Want to buy {land} for {land_price}? (y/n): ").lower()
                if choice == "y":
                    # Transaction occurs.
                    player.land.append(land)
                    self.sold_land.append(land)
                    print("Your owned land: ", player.land)
                    player.currency -= land_price
                    print(f"Your new balance: WTC{player.currency}")
                else:
                    print("No land for you, then.")
            else:
                print(f"It costs {land_price} and you have WTC{player.currency}. Can't buy.")
        # If it's been sold and the current player doesn't own it,
        # that must mean the other player owns it, so they should
        # pay rent.
        elif land not in player.land:
            land_rent = self.land_stats[land]['rent']
            print(f"Someone else owns this land, you have to pay WTC{land_rent} rent.")
            player.currency -= land_rent
            self.rent_box += land_rent
            print(f"Your new balance: WTC{player.currency}.")
        else:
            print("It's your land and it's looking good.")


    def location_event(self, player):
        """
        This function runs when the player moves for the turn.
        Every location they land on has its own function.
        """
        if player.location == 1:
            print(f"You arrive at the beginning square.")
        elif player.location == 2:
            # They'll get shown a Property Card here.
            print(f"You arrive at Python Hotel.")
            self.land_event("Python Hotel", player)
        elif player.location == 3:
            # They'll draw a card here.
            print(f"You arrive at a community chest.")
            self.comm_chest_draw(player, random.randint(1, 10))
        elif player.location == 4:
            print(f"You arrive at OOP-sy B&B.")
            self.land_event("OOP-sy B&B", player)
        elif player.location == 5:
            print(f"You trespass and get arrested – straight to jail.. (oh no!)")
            self.jail.append(player)
            self.jail_sequence(player, 3)
        elif player.location == 6:
            print(f"You arrive at a chance location.")
            self.chance_draw(player, random.randint(1, 10))
        elif player.location == 7:
            print(f"You arrive at CSS Heights.")
            self.land_event("CSS Heights", player)
        elif player.location == 8:
            print(f"You arrive at JS Inn.")
            self.land_event("JS Inn", player)
        elif player.location == 9:
            print(f"You arrive at Jail (luckily not as a prisoner.) Nothing important happens.")
        elif player.location == 10:
            print(f"You arrive at Memory Space.")
            self.land_event("Memory Space", player)
        elif player.location == 11:
            print(f"You arrive at RAM House.")
            self.land_event("RAM House", player)
        elif player.location == 12:
            print(f"You arrive at a community chest, and draw from it.")
            self.comm_chest_draw(player, random.randint(1, 10))
        elif player.location == 13:
            print(f"You arrive at Free Park. Best place to do nothing.")
        elif player.location == 14:
            print(f"You arrive at Cache de Cookie.")
            self.land_event("Cache de Cookie", player)
        elif player.location == 15:
            print(f"You arrive at a chance draw.")
            self.chance_draw(player, random.randint(1, 10))
        elif player.location == 16:
            print(f"You arrive at ROM-ance Inn.")
            self.land_event("ROM-ance Inn", player)


    def roll_die(self, player):
        """
        Lets the player roll the die, and returns the value,
        which is then used wherever we increment the player location.
        They can also save and quit from here.
        """
        while True:
            choice_1 = input(f"Roll the die, skip turn, save, or quit (r/skip/save/quit): ")
            if choice_1 == "r":
                result_1 = random.randint(1, 6)
                choice_2 = input(f"You rolled {result_1}. Roll again? (y/n): ")
                if choice_2 == "y":
                    result_2 = random.randint(1, 6)
                    print(f"You rolled {result_2}.")
                    return result_2
                if choice_2 == "n":
                    return result_1
            elif choice_1 == "skip":
                return 0
            elif choice_1 == "save":
                # Records which player is saving so it knows on whose turn to start
                # when loading.
                if player == self.player_two:
                    self.save_status["last to save"] = 2
                else:
                    self.save_status["last to save"] == 1
                pickle_out = open(f"savegame.pickle","wb")
                pickle.dump(self, pickle_out)
                print("Game saved.")
                pickle_out.close()
                pass
            elif choice_1 == "quit":
                print("See you next time.")
                quit()
            else:
                print("Please enter only a valid answer.")
                continue


    def turn(self, player):
        """
        This is a player turn. Either player_one or player_two is
        passed in as the player parameter.
        """
        # Any turn after loading a savegame checks if it was the second player
        # who saved the last game. If they did, the first player's turn is skipped.
        # Just loaded is set to False so this branch can't repeat until users load again.
        if self.save_status["just loaded"] == True and self.save_status["last to save"] == 2:
            print("As if! It was player 2's turn when you saved, remember?")
            self.save_status["just loaded"] = False
            return

        # If the opponent paid any rent last turn, it gets added
        # to your bank.
        if self.rent_box > 0:
            print(f"You collect WTC{self.rent_box} in rent.")
            player.currency += self.rent_box
            print(f"Your now have WTC{player.currency}.")
            self.rent_box = 0

        # Players still in jail play the jail sequence instead of a normal turn.
        if player in self.jail:
            self.jail_sequence(player, 3)
        # Otherwise, you can take your turn normally.
        else:
            outcome = self.roll_die(player)
            print(f"Moving {outcome} blocks.")
            player.location += outcome
            # This if checks whether they've passed the starting
            # point and takes action accordingly.
            if player.location > 16:
                player.location -= 16
                player.currency += 200
                print("You score a WTC200 bonus for passing the starting block.")
                print(f"Your new balance is {player.currency}")

            # If outcome is 0, that means they chose to skip the die roll.
            if outcome == 0:
                print("You take no action.")
            else:
                self.location_event(player)


    def play(self):

        """
        This function alternates between player turns for as long as
        both players still have money. As soon as someone doesn't have
        money, it announces the opponent as the winner.
        """
        load_or_new = input("Welcome to Terminopoly. New game or load game? (n/l): ")

        if load_or_new == "n":
            print("Both players start with 500WTC.")
            print("Good luck!")
        elif load_or_new == "l":
            pickle_in = open("savegame.pickle", "rb")
            self = pickle.load(pickle_in)
            # Records that the game has just been loaded so it modifies
            # the starting turn if necessary.
            self.save_status["just loaded"] = True
            print("Game successfully loaded.")
        else:
            print("Please enter only a valid value")
            return self.play()

        while True:
            print("\t\n>>> PLAYER ONE TURN STARTS <<<")
            self.turn(self.player_one)
            if self.player_one.currency <= 0:
                print("\t\n >>> PLAYER TWO WINS! <<<")
                print(f"Player one has {self.player_one.currency} left.")
                print(f"and an estate consisting of {self.player_one.land}.")
                break

            print("\t\n>>> PLAYER TWO TURN STARTS <<<")
            self.turn(self.player_two)
            if self.player_two.currency <= 0:
                print("\t\n>>> PLAYER ONE WINS! <<<")
                print(f"Player two has {self.player_two.currency} left.")
                print(f"and an estate consisting of {self.player_two.land}.")
                break


def main():
    """
    This loop creates instances of the classes and then commences a
    playthrough. At the end of the playthrough, the player has the choice
    to play again (i.e. continue the loop) or exit (break the loop
    and reach the end of the script).
    """
    while True:
        # Class instances are created.
        player_one = Player()
        player_two = Player()
        game = Terminopoly(player_one, player_two)
        # A playthrough commences.
        game.play()
        # When we've run through the play function, we give them
        # the option to replay.
        choice = input("Do you want to start a new game? (y/n): ")
        if choice == "y":
            print("Here we go again.")
            continue
        else:
            print("Until next time.")
            break


# Everything starts here.
main()