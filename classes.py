"""
IS 597PR Final Project: Analyzing the Effect of Player Positioning on Liar’s Dice under Complex Player Behavior

Contains Players, GameRules, and Record classes used to simulate liar's dice.

"""
import random
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display


class Players:
	"""
	A class to represent each player in the game
	"""
	all_players = []  # All players in the tournament
	active_players = []  # All players currently active in the game
	total_dice = 0  # Total dice in play between all active players
	total_faces = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}  # Count of all die faces
	
	def __init__(self, name: str, starting_hand_size: int, strategies: dict):
		"""
		Constructs all necessary attributes for the Players class
		Args:
			name (str): Name of the player for ease of reference
			starting_hand_size (int): The number of dice a player starts with
			strategies (dict): Values used to set a player's game strategies. Strategies include:
				- logical_bid (bool): Whether to use logical_bid (True) or random bidding behavior
				- challenge_threshold (int): Percent of dice the player will believe are in play (0-100), or -1 for random challenge behavior
				- preemptive_challenge (bool): Whether to challenge instead of bidding when the player believes their own bid may be challenged,
				but the previous bid is still believable
				- situational_aggression (bool): Whether to play more aggressively/defensively when the player has more/fewer dice than an opponent
		"""
		# Input validation
		for strategy, value in strategies.items():
			if strategy == 'challenge_threshold':
				if not type(value) is int:
					raise TypeError('challenge_threshold must be an integer')
				if value < -1 or value > 100:
					raise ValueError('challenge_threshold must either be -1 (for random behavior) or a number between 0 & 100')
			
			elif not isinstance(value, bool):
				raise TypeError(f'{strategy} must either be True or False')
		
		# Initialize instance attributes and update class attributes
		self.name = str(name)
		self.hand_size = starting_hand_size
		Players.total_dice += starting_hand_size
		self.my_roll = []
		self.my_faces = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
		
		self.logical_bid = strategies['logical_bid']
		self.challenge_threshold = strategies['challenge_threshold']
		self.preemptive_challenge = strategies['preemptive_challenge']
		self.situational_aggression = strategies['situational_aggression']
		
		self.all_players.append(self)
		self.active_players.append(self)
	
	def __str__(self) -> str:
		"""
		Returns the player's name when printing the Players instance
		Returns: str: The player's name
		"""
		return self.name
	
	@classmethod
	def roll_dice(cls, player_list: list):
		"""
		Roll dice for all players in a game
		Args:
			player_list (list[Players]): List of active players in the game in turn order
		"""
		# Resets rolls from any previous rounds
		cls.total_faces = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
		
		# Rolls dice for each player, updating relevant attributes
		for a_player in player_list:
			# Resets rolls from any previous rounds
			a_player.my_roll = []
			a_player.my_faces = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
			
			for x in range(a_player.hand_size):
				a_die = random.randint(1, 6)
				a_player.my_roll.append(a_die)
				a_player.my_faces[a_die] += 1
				Players.total_faces[a_die] += 1
			
			# Add rolls to roll_history Record
			Record.update_roll_history(a_player.name, a_player.my_roll, a_player.my_faces)
		
		# Adds a line break between rolls and first round in game_log
		Record.update_game_log('')
	
	def lose_a_die(self, player_list: list[Players]):
		"""
		Removes a die from a player after losing a challenge, possibly removing them from the game
		Args:
			player_list (list): The active players in the game
		"""
		if GameRules.reset_round_order:
			# Losing player moves to start of player_list to begin the next round
			n = player_list.index(self)
			updated_player_list = player_list[n:] + player_list[:n]
		else:
			# If not resetting round order, just copies player_list
			updated_player_list = player_list[:]
		
		if GameRules.sudden_death:
			# Removes a losing player from the round instead of losing a die
			Players.total_dice -= self.hand_size  # Remove player's dice from total_dice
			self.hand_size = 0  # Prevents player from rolling dice when not in a round
			updated_player_list.remove(self)  # Removes player from active players
		
		else:
			self.hand_size -= 1  # Removes a die from the player's hand
			Players.total_dice -= 1  # Removes a die from total_dice
			
			# Removes player from player_list if they lost their last die
			if self.hand_size <= 0:
				updated_player_list.remove(self)
		
		# Updates the list of active players still in the game
		Players.active_players = updated_player_list
	
	def reset_player(self, starting_hand_size: int):
		"""
		Resets player parameters between games
		Args:
			starting_hand_size (int): The number of dice each player starts with
		"""
		Players.active_players = Players.all_players  # Return all players to list of active players
		self.hand_size = starting_hand_size  # Refills hand with any lost dice
		Players.total_dice += starting_hand_size  # Refills total_dice with any lost dice
		# Clears any previous roll
		self.my_roll = []
		self.my_faces = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
		Record.game_log = ''  # Clears the game log
	
	@classmethod
	def delete_all_players(cls):
		"""
		Completely clears players between tournaments
		"""
		# Reset class variables
		cls.all_players = []
		cls.active_players = []
		cls.total_dice = 0
		cls.total_faces = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
		
		# Reset Record variables
		Record.game_log = ''
		Record.roll_history = []
		Record.bid_history = []
		Record.challenge_history = []
		Record.win_history = pd.DataFrame()


# ============================================================
class GameRules:
	"""
	A class to set basic rules of operation for the game
	"""
	randomize_order = False
	sudden_death = True
	reset_round_order = False
	
	def __init__(self, randomize_order=False, sudden_death=True, reset_round_order=False):
		"""
		Constructs all necessary attributes for the game
		Args:
			randomize_order (bool): Whether to randomize the turn order of each game
			sudden_death (bool): Whether players are immediately removed from the game when losing a challenge (True) or just lose a die (False)
			reset_round_order (bool): Whether the loser of a challenge should start the next round
		"""
		# Input validation
		for rule, value in {'randomize_order': randomize_order, 'sudden_death': sudden_death, 'reset_round_order': reset_round_order}.items():
			if not isinstance(value, bool):
				raise TypeError(f'{rule} must either be True or False')
		
		# Initialize class attributes
		GameRules.randomize_order = randomize_order
		GameRules.sudden_death = sudden_death
		GameRules.reset_round_order = reset_round_order


# ============================================================

class Record:
	"""
	A class to track the actions taken in games and the results of tournaments
	"""
	game_log = ''  # Readable output of rolls, bids, challenges, and game results
	roll_history = []  # Record of dice rolls
	bid_history = []  # Record of bids
	challenge_history = []  # Record of challenge results
	win_history = pd.DataFrame()  # Record of games won by each player
	print_by = 'Silent'  # Print method for the game_log
	
	def __init__(self, print_by: str = 'Silent'):
		"""
		Constructs all necessary attributes for the Record class
		Args:
			print_by (str): How to print the log of actions made in the game. Options are:
			- 'Line': Print each action as it occurs. This will slow the program down, but offers detailed view of what happens when.
			- 'Game': Print each game's log once the game has ended. Faster performance, but provides less granularity when debugging.
			- 'Silent': Does not print game logs at all.
		"""
		# Input validation
		if print_by not in ['Line', 'Game', 'Silent']:
			raise Exception('print_by must be one of "Line", "Game", or "Silent"')
		
		# Initialize class attributes
		Record.print_by = print_by
		Record.win_history = pd.DataFrame(columns=Players.all_players)
		Record.win_history.loc[len(Record.win_history)] = 0  # Adds a blank row to be copied
	
	@classmethod
	def update_game_log(cls, *messages):
		"""
		Adds game actions to the game_log
		Args:
			*messages: The message(s) to be added to the log
		"""
		if Record.print_by == 'Silent':
			# Does not maintain a game_log
			return
		
		# Concatenate messages onto one line
		full_message = ''
		for message in messages:
			full_message += str(message) + ' '
		
		if Record.print_by == 'Line':
			# Print the full action message
			print(full_message)
		
		elif Record.print_by == 'Game':
			# Add full action message to game_log to print once the game is over
			Record.game_log = Record.game_log + '\n' + full_message
	
	@classmethod
	def print_game_log(cls):
		"""
		If print_by == 'Game', prints a complete game_log once a game is over
		"""
		print(cls.game_log)
	
	@classmethod
	def update_roll_history(cls, name: str, dice_roll: list, dice_counts: dict):
		"""
		Adds dice roll to roll_history and game_log
		Args:
			name (str): The name of the player who made the roll
			dice_roll (list): List of dice faces rolled, e.g., [4, 2, 4, 5, 1]
			dice_counts (dict): Count of each die face in the roll, e.g., {1: 1, 2: 1, 3: 0, 4: 2, 5: 1, 6: 0}
		"""
		# Add roll to roll_history
		Record.roll_history.append([name, dice_counts])
		
		# Add roll to game_log
		cls.update_game_log(name, 'rolled', dice_roll)
	
	@classmethod
	def update_bid_history(cls, player: Players, bid: dict):
		"""
		Adds bid to bid_history and game_log
		Args:
			player (Players): The player making the bid
			bid (dict): A bid in the format {'Quantity', 'Face'}
		"""
		# Add bid to bid_history
		cls.bid_history.append({'Bidder': player.name, 'Quantity': bid['Quantity'], 'Face': bid['Face']})
		
		# Add bid to game_log
		cls.update_game_log(player, 'bids', bid)
	
	@classmethod
	def update_challenge_history(cls, challenger: Players, challengee: Players, valid_challenge: bool):
		"""
		Adds challenge to challenge_history and game_log
		Args:
			challenger (Players): The player who made the challenge
			challengee (Players): The player who was challenged
			valid_challenge (bool): True if the challenged bid was a lie; False if the bid was correct
		"""
		# Add challenge to game_log
		cls.update_game_log(challenger, 'challenges', challengee)
		
		if GameRules.sudden_death:
			loss_effect = 'is out of the game\n'
		else:
			loss_effect = 'loses a die\n'
		
		# Add challenge results to game_log and adds results to challenge_history
		if valid_challenge:
			cls.update_game_log('Liar!', challengee, loss_effect)
			cls.challenge_history.append({'Challenger': challenger.name, 'Challengee': challengee.name, 'Valid': 1, 'Invalid': 0})
		else:
			cls.update_game_log('Challenge fails;', challenger, loss_effect)
			cls.challenge_history.append({'Challenger': challenger.name, 'Challengee': challengee.name, 'Valid': 0, 'Invalid': 1})
	
	@classmethod
	def update_win_history(cls, winning_player: Players):
		"""
		Add win to win_history and game_log
		Args:
			winning_player (Players): The player that won the game
		"""
		df = cls.win_history
		df.loc[len(df)] = df.loc[len(df) - 1]  # Duplicate previous row
		
		column_index = list(df.columns).index(winning_player)  # Get index of winning_player
		df.iloc[len(df) - 1, column_index] += 1  # Increment win count
		
		# Add win to win_history
		cls.update_game_log(winning_player, 'wins!\n\n')
		
		if Record.print_by == 'Game':
			# Prints and resets game_record
			print(Record.game_log)
			Record.game_log = ''
	
	@classmethod
	def print_challenge_rates(cls):
		"""
		Prints each player's challenge metrics
		"""
		df = pd.DataFrame(data=Record.challenge_history)
		df = df.groupby('Challenger')  # Group by player name
		
		# Calculate in/valid challenge sums and success rate
		valid_sum = df['Valid'].sum()
		invalid_sum = df['Invalid'].sum()
		valid_rate = valid_sum / (valid_sum + invalid_sum)
		
		# Combine columns into one dataframe
		df = pd.concat([valid_sum, invalid_sum, valid_rate], axis=1)
		df.columns = ['Valid Challenges', 'Invalid Challenges', 'Valid Challenge Rate']
		
		# Display results
		display(df.sort_values(by='Valid Challenge Rate', ascending=False))
	
	@classmethod
	def print_win_rates(cls):
		"""
		Print each player's win history
		"""
		# Get final win tally
		df = Record.win_history.tail(1).transpose()
		
		df.rename(columns={df.columns[0]: 'Wins'}, inplace=True)
		
		# Calculate win rate for all games played
		game_count = df.sum().iloc[0]
		df['Win Rate'] = df['Wins'] / game_count
		
		# Display results
		display(df.sort_values('Win Rate', ascending=False))
	
	@classmethod
	def plot_win_rates(cls):
		"""
		Plots each player's win rates for the tournament
		"""
		df = Record.win_history
		
		# Divide win totals by number of games played
		win_rates = df.div(df.index, axis='index')
		
		# Plot results
		win_rates.plot(title="Player Win Rates")
		plt.xlabel("Number of Games")
		plt.ylabel("Win Rate")
		plt.show()
