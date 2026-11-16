"""TODO: DOCSTRING"""
import random
import pandas as pd
import matplotlib.pyplot as plt


class AllPlayers:
	# TODO: Document
	
	all_players = []
	total_dice = 0
	total_faces = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
	
	def __init__(self, name: str, starting_hand_size: int, liar_threshold=-1, prefer_bid=False, conservative_increase=False):
		self.name = name
		
		self.hand_size = starting_hand_size
		AllPlayers.total_dice += starting_hand_size
		self.my_roll = []
		self.my_faces = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
		
		self.prefer_bid = prefer_bid  # NOTE: Remove if unused
		self.liar_threshold = liar_threshold
		self.conservative_increase = conservative_increase
		
		self.all_players.append(self)
	
	# TODO: Make this more useful
	def __str__(self):
		return self.name
	
	def __repr__(self):
		return self.name
	
	@classmethod
	def roll_dice(cls, player_list: list):
		"""
		Roll a specified number of dice, each returning a random integer from 1 to 6.

		:return: A list of integers representing dice values.

		"""
		# NOTE: Update docs
		cls.total_faces = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
		
		for a_player in player_list:
			
			a_player.my_roll = []
			a_player.my_faces = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
			for x in range(a_player.hand_size):
				a_die = random.randint(1, 6)
				a_player.my_roll.append(a_die)
				a_player.my_faces[a_die] += 1
				AllPlayers.total_faces[a_die] += 1
			
			Record.roll(a_player.name, a_player.my_roll, a_player.my_faces)
	
	def lose_a_die(self, player_list):
		self.hand_size -= 1
		AllPlayers.total_dice -= 1
		
		# Losing player moves to start of player_list to begin the next round
		n = player_list.index(self)
		updated_player_list = player_list[n:] + player_list[:n]
		
		# Removes player from player_list if they lost their last die
		if self.hand_size <= 0:
			updated_player_list.remove(self)
		
		return updated_player_list
	
	def reset_player(self, starting_hand_size: int):
		self.hand_size = starting_hand_size
		AllPlayers.total_dice += starting_hand_size
		self.my_roll = []
		self.my_faces = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
		Record.game_log = ''


class Record:
	# TODO: Document
	
	game_number = 0
	round_number = 0
	game_log = ''
	roll_history = pd.DataFrame(columns=['Player', '1s', '2s', '3s', '4s', '5s', '6s'])
	bid_history = pd.DataFrame(columns=['Bidder', 'Quantity', 'Die Face'])
	challenge_history = pd.DataFrame(columns=['Challenger', 'Challengee', 'Valid', 'Invalid'])
	win_history = pd.DataFrame()
	
	def __init__(self):
		Record.win_history = pd.DataFrame(columns=AllPlayers.all_players)
		
		Record.win_history.loc[len(Record.win_history)] = 0
	
	@classmethod
	def roll(cls, name: str, roll: list, roll_counts: dict):
	# TODO: Optimize somehow
		if False:
			row = list(roll_counts.values())
			row.insert(0, name)
			
			df = cls.roll_history
			df.loc[len(df)] = row
		
		cls.update_game_log(name, 'rolled', roll)
	
	@classmethod
	def bid(cls, player: AllPlayers, bid: dict | int):
		#TODO: Optimize somehow
		if False:
			df = cls.bid_history
			
			if isinstance(bid, dict):
				df.loc[len(df)] = [player, bid['Quantity'], bid['Face']]
			else:
				df.loc[len(df)] = [player, bid, 'NA']
		
		cls.update_game_log(player, 'bids', bid)
	
	@classmethod
	def challenge(cls, challenger: AllPlayers, challengee: AllPlayers, valid_challenge: bool):
		cls.update_game_log(challenger, 'challenges', challengee)
		df = cls.challenge_history
		
		if valid_challenge:
			cls.update_game_log('Liar!', challengee, 'loses a die\n')
			df.loc[len(df)] = [challenger, challengee, 1, 0]
		else:
			cls.update_game_log('Challenge fails;', challenger, 'loses a die\n')
			df.loc[len(df)] = [challenger, challengee, 0, 1]
	
	@classmethod
	def win(cls, winning_player: AllPlayers):
		df = cls.win_history
		df.loc[len(df)] = df.loc[len(df) - 1]  # Duplicate previous row
		
		column_index = list(df.columns).index(winning_player)  # Get index of winning_player
		df.iloc[len(df) - 1, column_index] += 1  # Increment win count
		
		cls.update_game_log(winning_player, 'wins!\n\n')
	
	@classmethod
	def plot_win_rates(cls):
		df = Record.win_history
		
		win_rates = df.div(df.index, axis='index')
		
		win_rates.plot(title="Player Win Rates")
		plt.xlabel("Number of Games")
		plt.ylabel("Win Rate")
		plt.show()
	
	@classmethod
	def update_game_log(cls, *messages):
		for message in messages:
			cls.game_log += str(message) + ' '
		cls.game_log += '\n'
	
	@classmethod
	def print_game_log(cls):
		print(cls.game_log)
