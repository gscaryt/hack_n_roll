import random
import json

class Cloud:
    '''Stores the Tokens on the Cloud.'''
    encrypted = []
    cracked = [2,3,4,5,6,7,8,9,10,11,12]


class Player:
    def __init__(self, speed=100):
        self.speed = speed
        self.encrypted = []
        self.cracked = []
        self.times_roll = 0

    def roll_dice(self):
        return [random.randint(1,6), random.randint(1,6)]


class Sender(Player):
    def __init__(self, speed=100):
        super().__init__(speed)
        self.encrypted = [2,3,4,5,6,7,8,9,10,11,12]
        self.priority = [2,12,3,11,4,10,5,9,6,8,7]
        self.times_send_encrypted = 0
        self.times_remove_token = 0

    def is_winner(self):
        '''Returns Boolean for Sender winning conditions'''
        return self.encrypted == []

    def send_encrypted(self, value):
        '''
        Sends one Encrypted Token with 'value' to the Cloud.
        value: int (sum of the dice)
        '''
        if value in self.encrypted:
            self.encrypted.remove(value)
            Cloud.encrypted.append(value)
            self.times_send_encrypted += 1
            return True

    def remove_token(self, value, cracker):
        '''
        Removes one token with 'value' from the cracker to the Cloud.
        value: int (2-12)
        '''
        if value in cracker.encrypted:
            cracker.encrypted.remove(value)
            Cloud.encrypted.append(value)
            self.times_remove_token += 1
            return True
        elif value in cracker.cracked:
            cracker.cracked.remove(value)
            Cloud.cracked.append(value)
            return True

    def strategy_basic(self, cracker, roll):
        done = False
        if roll[0] == roll[1]:
            if sum(roll) in self.encrypted and sum(roll) in self.priority[:4]:
                self.send_encrypted(sum(roll))
                done = True
            else:
                for value in self.priority:
                    if self.remove_token(value, cracker):
                        done = True
                        break
        if not done:
            self.send_encrypted(sum(roll))

    def tactic_block(self, cracker, value, threshold, roll):
            return (
                sum(roll) == value 
                and value not in cracker.cracked 
                and len(self.encrypted) > threshold
                )

class Cracker(Player):
    def __init__(self, speed=100):
        super().__init__(speed)
        self.priority = [2,12,3,11,4,10,5,9,6,8,7]
        self.times_get_encrypted = 0
        self.times_get_cracked = 0

    def is_winner(self):
        '''Returns boolean for Cracker winning conditions'''
        data = self.encrypted + self.cracked
        return set(data) == set((2,3,4,5,6,7,8,9,10,11,12))

    def get_encrypted(self, value):
        '''
        Get one Encrypted Token with 'value' from the Cloud.
        value: int (sum of the dice)
        '''
        if value in Cloud.encrypted:
            Cloud.encrypted.remove(value)
            self.encrypted.append(value)
            self.times_get_encrypted += 1
            return True
    
    def get_cracked(self, cracked_data):
        '''
        Get one Cracked Token with 'value' from the Cloud.
        value: int (sum of the dice)
        '''
        if cracked_data in Cloud.cracked:
            Cloud.cracked.remove(cracked_data)
            self.cracked.append(cracked_data)
            self.times_get_cracked += 1
            return True

    def strategy_basic(self, roll):
        done = False
        if roll[0] == roll[1]:
            for value in self.priority:
                if (value in Cloud.cracked
                    and value not in self.cracked
                    and value not in self.encrypted
                ):
                    self.get_cracked(value)
                    done = True
                    break
        if not done:
            self.get_encrypted(sum(roll))

    def tactic_counter_block(self, threshold):
        if len(set(self.encrypted + self.cracked)) > threshold:
            for value in (7,6,8,5,9):
                if (value not in self.cracked
                    and value not in self.encrypted
                ):
                    self.priority.remove(value)
                    self.priority.insert(0, value)
                break

class Results:
    rounds = []

def reset(Cloud, sender, cracker):
    Cloud.encrypted = []
    Cloud.cracked = [2,3,4,5,6,7,8,9,10,11,12]
    del sender
    del cracker


def game(round, sample):
    # Set the Cloud and Players
    sender = Sender(75)
    cracker = Cracker(75)
    turn = 1
    if round == sample:
        with open('sample_game.txt', 'w') as sample_game:
            sample_game.write('')

    while True:

        # Sender
        if random.randint(1,99) < sender.speed:
            s_roll = sender.roll_dice()
            if sender.tactic_block(cracker, 7, 1, s_roll):
                pass
            elif sender.tactic_block(cracker, 6, 5, s_roll):
                pass
            elif sender.tactic_block(cracker, 8, 5, s_roll):
                pass
            else:
                sender.strategy_basic(cracker, s_roll)
            sender.times_roll += 1
        else:
            s_roll = '[None]'

        # Cracker
        if random.randint(1,99) < cracker.speed:
            c_roll = cracker.roll_dice()
            cracker.strategy_basic(c_roll)
            cracker.tactic_counter_block(6)
            cracker.times_roll += 1
        else:
            c_roll = '[None]'
        
        # Get Sample
        if round == sample:
            with open('sample_game.txt', 'a') as sample_game:
                sample_game.write(
                    f'Sender Roll:  {s_roll} | {sender.encrypted} | {Cloud.encrypted} | {cracker.encrypted}\n'
                    f'Cracker Roll: {c_roll} | {sender.cracked} | {Cloud.cracked} | {cracker.cracked}\n\n'
                )

        # Winning Conditions
        if sender.is_winner():
            winner = "Sender"
            if round == sample:
                with open('sample_game.txt', 'a') as sample_game:
                    sample_game.write(
                        f'Sender wins.'
                    )
            break
        elif cracker.is_winner():
            winner = "Cracker"
            if round == sample:
                with open('sample_game.txt', 'a') as sample_game:
                    sample_game.write(
                        f'Cracker wins.'
                    )
            break
        elif turn == 300:
            # This is too long. It shouldn't reach here.
            winner = "None"
            break
        else:
            turn += 1

    rounds = {
        "Round": round, 
        "Winner": winner, 
        "Sender": (sender.times_roll, sender.times_send_encrypted, sender.times_remove_token),
        "Cracker": (cracker.times_roll, cracker.times_get_encrypted, cracker.times_get_cracked),
        }
    Results.rounds.append(rounds)

    '''Reset the Game State'''
    reset(Cloud, sender, cracker)


def run(sample_size):
    for round in range(sample_size):
        game(round, sample_size/2)
    
    if True: # Get Averages
        send_wins = 0
        crack_wins = 0
        none_wins = 0
        total_sender_rolls = 0
        total_send_encrypted = 0
        total_remove_token = 0
        total_cracker_rolls = 0
        total_get_encrypted = 0
        total_get_cracked = 0
        for dictionary in Results.rounds:
            total_sender_rolls += dictionary["Sender"][0]
            total_send_encrypted += dictionary["Sender"][1]
            total_remove_token += dictionary["Sender"][2]
            total_cracker_rolls += dictionary["Cracker"][0]
            total_get_encrypted += dictionary["Cracker"][1]
            total_get_cracked += dictionary["Cracker"][2]
            for value in dictionary.values():
                if value == 'Sender':
                    send_wins += 1
                elif value == 'Cracker':
                    crack_wins += 1
                elif value == 'None':
                    none_wins += 1
        average_sender_rolls = total_sender_rolls/sample_size
        average_cracker_rolls = total_cracker_rolls/sample_size
        average_send_encrypted = total_send_encrypted/sample_size
        average_remove_token = total_remove_token/sample_size
        average_get_encrypted = total_get_encrypted/sample_size
        average_get_cracked = total_get_cracked/sample_size

    with open('data.txt', 'w') as data_file:
        # Write all Rounds Data
        data_file.write(
            f'# Sample Size: {sample_size}\n'
            f'# Sender wins: {send_wins} | Cracker wins: {crack_wins}\n'
            f'# Sender Average | Rolls: {average_sender_rolls} | Sent Encrypted {average_send_encrypted} | Removed Token {average_remove_token}\n'
            f'# Cracker Average | Rolls: {average_cracker_rolls} | Get Encrypted {average_get_encrypted} | Get Cracked {average_get_cracked}\n'
            f'#\n'
            )
        
        data_file.write('[Round, Winner, Sender(Rolls, SendEncr, RemoveDat), Cracker(Rolls, GetEncr, GetCrac)]\n')
        for dictionary in Results.rounds:
            data_file.write(f'{list(dictionary.values())}\n')


if __name__ == "__main__":
    run(10000)