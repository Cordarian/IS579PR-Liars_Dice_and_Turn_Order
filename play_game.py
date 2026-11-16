"""DOCSTRING"""

from game_rules import *
from classes import *
from collections import Counter
import pandas as pd
from IPython.display import display  # NOTE: Remove before submission probably
import matplotlib.pyplot as plt


def initialize_players(dice_count: int, player_count: int, strategies=None):
	player_list = []
	player_names = ['Alice', 'Bob', 'Charlie', 'Dan', 'Eve', 'Frank', 'Grace', 'Heidi', 'Ivan', 'Judy']
	
	AllPlayers.total_dice = 0
	AllPlayers.total_faces = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
	
	for i in range(0, player_count):
		player_list.append(AllPlayers(player_names[i], dice_count, liar_threshold=-1, conservative_increase=True))
	
	return player_list


def reset_players(dice_count: int):
	AllPlayers.total_dice = 0
	AllPlayers.total_faces = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
	
	for player in AllPlayers.all_players:
		player.reset_player(dice_count)


def play_round(round_order):
	previous_bid = None
	previous_player = None
	AllPlayers.roll_dice(round_order)
	
	while True:  # Play continues until a challenge breaks the loop
		for current_player in round_order:
			if len(round_order) == 2 and AllPlayers.total_dice == 2:
				# Use endgame rules for 2 players with 1 die each
				new_bid = generate_bid_endgame(current_player, previous_bid)
				decision = consider_challenging(current_player, previous_bid, new_bid, endgame=True)
			else:
				# Use normal rules for all other rounds
				new_bid = generate_bid(current_player, previous_bid)
				decision = consider_challenging(current_player, previous_bid, new_bid)
			
			if decision == 'Liar':
				return call_liar(previous_bid, previous_player, current_player, round_order)
			else:
				Record.bid(current_player, new_bid)
				previous_bid = new_bid
			
			previous_player = current_player


def play_game(active_players: list, dice_count: int, randomize_order=False):
	reset_players(dice_count)
	if randomize_order:
		random.shuffle(active_players)
	
	while len(active_players) > 1:
		active_players = play_round(active_players)
	
	return active_players[0]


def play_tournament(game_count: int, player_count: int, dice_count: int, strategies=None, randomize_order=False):
	if game_count < 1:
		raise ValueError("Game count must be at least 1")
	if player_count < 2 or dice_count <= 0:
		raise ValueError("Game must include at least 2 players with 1 or more dice")
	
	player_list = initialize_players(dice_count, player_count)
	Record()
	
	for game in range(game_count):
		winner = play_game(player_list, dice_count, randomize_order)
		Record.win(winner)
		Record.print_game_log()




if __name__ == '__main__':
	num_games = 1000
	num_players = 5
	num_dice = 5
	
	play_tournament(num_games, num_players, num_dice, randomize_order=False)
	Record.plot_win_rates()
