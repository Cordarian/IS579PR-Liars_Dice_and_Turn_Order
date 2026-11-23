"""
IS 597PR Final Project: Analyzing the Effect of Player Positioning on Liar’s Dice under Complex Player Behavior

This module contains functions to simulate the game Liar's Dice with different game conditions, rules, and player strategies.

Based on the original project 'Analyzing Win Probabilities in the Dice Game
"Liar's Dice" Using Monte Carlo Simulations' by Yueyue Lin & Jiajing Liang:
https://github.com/Yena830/Liars_dice_IS597PR

"""
from player_actions import *


def initialize_players(player_count: int, dice_count: int, strategies: list):
	"""
	Creates instances of the Players class to use in game simulations
	
	Args:
		player_count (int): The number of players to include in the game
		dice_count (int): The number of dice each player starts with
		strategies (list): List of lists of game strategies to be used by each player. Strategies include:
				- logical_bid (bool): Whether to use logical_bid (True) or random bidding behavior
				- challenge_threshold (int): Percent of dice the player will believe are in play (0-100), or -1 for random challenge behavior
				- preemptive_challenge (bool): Whether to challenge instead of bidding when the player believes their own bid may be challenged,
				but the previous bid is still believable
				- situational_aggression (bool): Whether to play more aggressively/defensively when the player has more/fewer dice than an opponent
	"""
	# Resets any existing players from previous tournaments
	Players.total_dice = 0
	Players.total_faces = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
	Players.delete_all_players()
	
	player_names = ['Alice', 'Bob', 'Charlie', 'Dan', 'Eve', 'Frank', 'Grace', 'Heidi', 'Ivan', 'Judy']
	
	# Creates each player using their designated strategies
	for x in range(0, player_count):
		Players(player_names[x], dice_count, strategies[x])


def package_strategies(logical_bid=False, challenge_threshold=-1, preemptive_challenge=False, situational_aggression=False) -> dict:
	"""
	Loads provided strategies into a dictionary, using default values for unspecified strategies
	
	Args:
		logical_bid (bool): Whether to use logical_bid (True) or random bidding behavior
		challenge_threshold (int): Percent of dice the player will believe are in play (0-100), or -1 for random challenge behavior
		preemptive_challenge (bool): Whether to use preemptive_challenge behavior
		situational_aggression (bool): Whether to use situational_aggression behavior

	Returns: dict: Dictionary of strategies
	"""
	return {'logical_bid'           : logical_bid,
			'challenge_threshold'   : challenge_threshold,
			'preemptive_challenge'  : preemptive_challenge,
			'situational_aggression': situational_aggression}


def reset_players(dice_count: int):
	"""
	Resets player variables between games
	Args:
		dice_count (int): The number of dice each player starts with
	"""
	# Reset class variables
	Players.total_dice = 0
	Players.total_faces = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
	
	# Resets each player instance
	for player in Players.all_players:
		player.reset_player(dice_count)


def play_round():
	"""
	Simulates one game round, with players making bids until someone challenges by calling 'Liar'
	"""
	previous_bid = None
	previous_player = None
	round_order = Players.active_players
	Players.roll_dice(round_order)
	
	while True:  # Play continues until a challenge breaks the loop
		for current_player in round_order:
			# Generate a potential bid
			new_bid = generate_bid(current_player, previous_bid)
			# Decides whether to challenge the previous bid or make a new bid
			decision = consider_challenging(current_player, previous_bid, new_bid)
			
			if current_player.preemptive_challenge:
				# Cannot challenge before a bid is made, and doesn't reevaluate when already calling 'Liar'
				if previous_bid is not None and new_bid != 'Liar':
					# If current_player would not believe their own potential bid, challenges the previous player instead
					decision = evaluate_bid(new_bid, current_player, own_bid=True)
			
			# Either submits a new bid or challenges the previous player
			if decision != 'Liar':
				Record.update_bid_history(current_player, new_bid)
				previous_bid = new_bid
				previous_player = current_player
			else:
				call_liar(previous_bid, previous_player, current_player, round_order)
				return  # Ends the round


def play_game(dice_count: int):
	"""
	Simulates one game of liar's dice
	Args:
		dice_count (int): The number of dice each player starts with
	"""
	reset_players(dice_count)  # Resets players between games
	
	# Randomizes player turn order if randomize_order == True
	if GameRules.randomize_order:
		random.shuffle(Players.active_players)
	
	# Simulates game rounds until only one active player remains
	while len(Players.active_players) > 1:
		play_round()
	
	# Adds the winning player to win_history Record
	Record.update_win_history(Players.active_players[0])


def play_tournament(game_count: int, player_count: int, dice_count: int, strategies: list[dict], print_by: str = 'Silent'):
	"""
	Simulates consecutive games of liar's dice
	Args:
		game_count (int): The number of games to run in the tournament
		player_count (int): The number of players to include in each game
		dice_count (int): The number of dice each player starts with
		strategies (list[dict]): List of dictionary of play strategies to be used by each player
		print_by (str): How to print the log of actions made in the game. Options are:
			- 'Line': Print each action as it occurs. This will slow the program down, but offers detailed view of what happens when.
			- 'Game': Print each game's log once the game has ended. Faster performance, but provides less granularity when debugging.
			- 'Silent': Does not print game logs at all.
	"""
	# Input validation
	if game_count < 1:
		raise ValueError("Game count must be at least 1")
	if player_count < 2 or dice_count <= 0:
		raise ValueError("Game must include at least 2 players with 1 or more dice")
	
	# Create Players instances
	initialize_players(player_count, dice_count, strategies)
	Record(print_by=print_by)  # Sets print_by mode
	
	# Simulates each game in the tournament
	for game in range(game_count):
		play_game(dice_count)


if __name__ == '__main__':
	num_games = 200
	num_players = 5
	num_dice = 5
	
	player_strategies = []
	
	for i in range(num_players):
		if i == 0:
			player_strategies.append(package_strategies(
					logical_bid=False,
					challenge_threshold=17,
					preemptive_challenge=False,
					situational_aggression=False))
		else:
			player_strategies.append(package_strategies(
					logical_bid=False,
					challenge_threshold=-1,
					preemptive_challenge=False,
					situational_aggression=False))
	
	GameRules(
			randomize_order=False,
			reset_round_order=False,
			sudden_death=False)
	
	play_tournament(num_games, num_players, num_dice, player_strategies, print_by='Line')
	
	Record.plot_win_rates()
	Record.print_win_rates()
