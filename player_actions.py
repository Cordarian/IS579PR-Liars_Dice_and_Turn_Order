"""
IS 597PR Final Project: Analyzing the Effect of Player Positioning on Liar’s Dice under Complex Player Behavior

Contains functions representing the actions available to players during the game, including bidding, challenging, and deciding which to do on their
turn.

"""
from classes import *


def make_opening_bid(this_player: Players, top_faces: list[int], total_dice: int, max_known_quantity: int) -> dict[str, int]:
	"""
	Makes the opening bid in a round.
	Args:
		this_player (Players): The current player making the bid
		top_faces (list[int]): A list of preferred die faces to bid on. top_faces lists the faces the player has the most of in their hand
		total_dice (int): The total number of dice in play between all active players
		max_known_quantity (int): The highest quantity of any die face(s) this_player has in their hand

	Returns: dict: The player's opening bid in the format {'Quantity', 'Face'}
	"""
	# Random behavior
	if not this_player.logical_bid:
		# Bids a quantity between 2 and the total number of dice in play
		possible_quantities = [2, total_dice]
		bid_quantity = random.randint(min(possible_quantities), max(possible_quantities))
		# Bids a random die face
		bid_face = random.randint(1, 6)
		return {'Quantity': bid_quantity, 'Face': bid_face}
	
	# Non-random behavior
	# Chooses the smallest die face the player has the most of in their hand
	face_value = top_faces[0]
	
	# Bidding quantity starts between the quantity of the face the player has in their own hand and the amount they expect to be in play,
	# assuming perfect roll distribution
	average_quantity = total_dice // 6
	
	# Prevents bidding 0 if the average_quantity is low
	if average_quantity == 0:
		average_quantity = 1
	
	possible_quantities = [max_known_quantity, average_quantity]
	bid_quantity = random.randint(min(possible_quantities), max(possible_quantities))
	
	return {'Quantity': bid_quantity, 'Face': face_value}


def random_bid_increase(bid_quantity: int, bid_face: int, total_dice: int) -> dict[str, int]:
	"""
	Randomly increases the bid for players not using logical_bid behavior.
	This function is largely based on Lin & Liang's original project.
	Args:
		bid_quantity (int): The quantity of the previous bid
		bid_face (int): The die face of the previous bid
		total_dice (int): The total number of dice in play between all active players

	Returns: dict: A bid in the format {'Quantity', 'Face'}
	"""
	# Randomly increase the bid quantity
	possible_quantities = [bid_quantity + 1, total_dice]
	increased_quantity = random.randint(min(possible_quantities), max(possible_quantities))
	
	# Randomly increase the bid face from those available
	possible_higher_faces = [bid_face + 1, 6]
	increased_face = random.randint(min(possible_higher_faces), max(possible_higher_faces))
	
	# Randomly decrease the bid face from those available
	possible_lower_faces = [1, bid_face - 1]
	decreased_face = random.randint(min(possible_lower_faces), max(possible_lower_faces))
	
	available_strategies = [
		'increase_face',
		'increase_quantity',
		'increase_both',
		'increase_quantity_decrease_face']
	
	# Remove unavailable bid strategies from consideration
	if bid_face == 6:
		# If bid_face is 6, we cannot increase_face or increase_both
		available_strategies.remove('increase_face')
		available_strategies.remove('increase_both')
	elif bid_face == 1:
		# If bid_face is 1, we cannot increase_quantity_decrease_face
		available_strategies.remove('increase_quantity_decrease_face')
	if bid_quantity == total_dice:
		# If the bid_quantity cannot be increased, increase_face is the only option
		available_strategies = ['increase_face']
	
	# Choose an available strategy at random
	use_strategy = random.choice(available_strategies)
	
	# Select a bid quantity and face based on chosen use_strategy
	if use_strategy == 'increase_face':
		return {'Quantity': bid_quantity, 'Face': increased_face}
	elif use_strategy == 'increase_quantity':
		return {'Quantity': increased_quantity, 'Face': bid_face}
	elif use_strategy == 'increase_both':
		return {'Quantity': increased_quantity, 'Face': increased_face}
	elif use_strategy == 'increase_quantity_decrease_face':
		return {'Quantity': increased_quantity, 'Face': decreased_face}
	else:
		raise Exception('Path should be unreachable')


def generate_bid(this_player: Players, previous_bid: dict[str, int] | None) -> dict[str, int] | str:
	"""
	Makes an opening bid or increases from an existing bid
	Args:
		this_player (Players): The current player making the bid
		previous_bid (dict[str, int] | None): The previous player's bid, or None if this is the first bid of the round

	Returns:
		dict: A bid in the format {'Quantity', 'Face'}
		str: The string 'Liar' if no further bids are possible
	"""
	# Gets the die face(s) the player has the most of in their hand and what quantity they have of those face(s)
	max_known_quantity = int(max(this_player.my_faces.values()))
	top_faces = sorted(a_face for a_face, count in this_player.my_faces.items() if count == max_known_quantity)
	total_dice = Players.total_dice
	
	# First bid
	if previous_bid is None:
		return make_opening_bid(this_player, top_faces, total_dice, max_known_quantity)
	
	# Unpacks a previous bid
	bid_quantity, bid_face = previous_bid.values()
	
	# Must challenge if the bid cannot be increased further
	if bid_quantity >= total_dice and bid_face == 6:
		return 'Liar'
	
	# Random behavior
	if not this_player.logical_bid:
		return random_bid_increase(bid_quantity, bid_face, total_dice)
	
	# Non-random behaviors
	# Increase die face to the smallest face in top_faces, keeping the same quantity
	for this_face in top_faces:
		if this_face > bid_face:
			return {'Quantity': bid_quantity, 'Face': this_face}
	
	# Attempt to increase the bid quantity
	raised_quantity = min(bid_quantity + 1, total_dice)
	
	# If increasing the bid quantity, player uses their best top_face
	if raised_quantity > bid_quantity:
		return {'Quantity': raised_quantity, 'Face': top_faces[0]}
	
	# If the quantity cannot be increased, must increase the face using a non-top_face
	else:
		# Gets count of all faces the player has
		face_preferences = this_player.my_faces
		
		# Sorts die faces by decreasing quantity in the player's hand
		# Ref: https://www.geeksforgeeks.org/python/sort-python-dictionary-by-value/
		face_preferences = {key: value for key, value in sorted(face_preferences.items(), reverse=True, key=lambda item: item[1])}
		
		# Bids using a face higher than the bid_face that the player has the most of
		for this_face in face_preferences:
			if this_face > bid_face:
				return {'Quantity': raised_quantity, 'Face': this_face}
	
	raise Exception('Path should be unreachable')


def consider_challenging(current_player: Players, opponents_bid: dict[str, int] | None, own_bid: dict[str, int] | str) -> dict[str, int] | str:
	"""
	Decides whether to challenge the previous bid or submit a new one
	Args:
		current_player (Players): The current player making the challenge/bid
		opponents_bid (dict | None): The previous player's bid, or None if this is the first bid of the round
		own_bid (dict | str): The current player's potential bid if they do not challenge, or the string 'Liar' if no further bids are possible

	Returns:
		dict: If not challenging, returns the current player's unchanged potential bid
		str: If challenging, the string 'Liar'
	"""
	# Cannot challenge before a bid is made
	if opponents_bid is None:
		return own_bid
	
	# Must challenge if the bid cannot be increased
	if own_bid == 'Liar':
		return 'Liar'
	
	# Random challenge behavior
	if current_player.challenge_threshold == -1:
		bid_quantity, bid_face = opponents_bid.values()
		own_roll = current_player.my_faces
		
		if bid_quantity <= own_roll[bid_face]:
			# Does not challenge if current_player knows a bid is true
			return own_bid
		else:
			# Randomly bids or challenges
			return random.choice([own_bid, 'Liar'])
	
	# Non-random challenge behavior
	else:
		# Evaluates the likelihood of the bid being true or not
		return evaluate_bid(opponents_bid, current_player)


def evaluate_bid(bid: dict[str, int], current_player: Players, own_bid=False) -> dict[str, int] | str:
	"""
	Evaluates the likelihood of a bid being true based on the player's challenge_threshold and aggression strategy
	Args:
		bid (dict): The bid being evaluated, in the format {'Quantity', 'Face'}
		current_player (Players): The player evaluating the bid
		own_bid (bool): True if the player is evaluating the likelihood of their own potential bid being true, or False if evaluating the bid of the
		previous player when deciding to challenge

	Returns:
		dict: If not challenging, returns the bid unchanged
		str: If challenging, returns the string 'Liar'
	"""
	bid_quantity, bid_face = bid.values()
	own_roll = current_player.my_faces
	unknown_dice_count = Players.total_dice - current_player.hand_size
	
	# Get count of bid_face that would have to be in other players' hands for the bid to be true
	remaining_bid_quantity = bid_quantity - own_roll[bid_face]
	
	# Calculates the number of dice in other players' hands the current player is willing to believe are a given face based on the player's
	# challenge_threshold
	threshold_percent = current_player.challenge_threshold / 100
	believable_remaining_quantity = unknown_dice_count * threshold_percent
	
	if not own_bid:
		# An opponent presumably has at least 1 die of the face they are bidding
		believable_remaining_quantity = max(1, believable_remaining_quantity)
	
	if current_player.situational_aggression:
		# Adjusts the believable quantity based on the die count dis/advantage the player has
		believable_remaining_quantity = adjust_aggression(believable_remaining_quantity, current_player, own_bid)
	
	# Challenge if the bid is higher than the believable quantity
	if remaining_bid_quantity > believable_remaining_quantity:
		return 'Liar'
	else:
		return bid


def adjust_aggression(believable_dice_count: int, current_player: Players, own_bid: bool) -> int:
	"""
	Adjusts the number of a die face a player is willing to believe are in play based on whether they have more or fewer dice than other players.
	This function is used when deciding whether to challenge the previous player's bid, and when determining the likelihood of the next player
	challenging a potential bid from the current player.
	A player that knows more of the game state than an opponent plays more aggressively; a player that knows less of the game state plays more
	defensively.
	E.g., 	if a player has fewer dice than an opponent, they are more willing to believe an opponent's bid since they know more of the dice in play
	than
	the current player.
	
	Args:
		believable_dice_count (int): The number of dice of a given face the current player is willing to believe are in other players' hands based
		on their challenge_threshold
		current_player (Players): The player evaluating a bid
		own_bid (bool): True if the player is evaluating the likelihood of the player's own potential bid being true, or False if evaluating the
		bid of the previous player

	Returns: int: The adjusted believable dice count
	"""
	
	# Gets the number of dice current_player has and their location in the active_player list
	own_hand_size = current_player.hand_size
	current_index = Players.active_players.index(current_player)
	
	if own_bid:
		# Gets the number of dice the next player has in their hand
		opponent_hand_size = Players.active_players[(current_index + 1) % len(Players.active_players)].hand_size
	else:
		# Gets the number of dice the previous player has in their hand
		opponent_hand_size = Players.active_players[current_index - 1].hand_size
	
	# Adjusts believable_dice_count up or down based on whether the current player or their opponent has greater knowledge of the dice in play
	adjust_by = own_hand_size - opponent_hand_size
	believable_dice_count -= adjust_by
	
	return believable_dice_count


def call_liar(challenged_bid: dict[str, int], previous_player: Players, current_player: Players, player_list: list):
	"""
	Determines the winner of a challenge when one player calls 'liar' on another
	Args:
		challenged_bid (dict): The bid being challenged
		previous_player (Players): The player being challenged
		current_player (Players): The player who initiated the challenge
		player_list (list): The active players in the game
	"""
	# Gets the challenged bid and the count of dice actually rolled
	bid_quantity, bid_face = challenged_bid.values()
	dice_in_play = Players.total_faces
	
	# Challenge succeeds; the bid was a lie
	if bid_quantity > dice_in_play[bid_face]:
		challenge_result = 'Liar!'
	# Challenge fails; the bid was valid
	else:
		challenge_result = 'Challenge fails'
	
	# Update the challenge_record and remove a die from the losing player, potentially removing them from the game
	if challenge_result == 'Liar!':
		Record.update_challenge_history(current_player, previous_player, valid_challenge=True)
		previous_player.lose_a_die(player_list)
	else:
		Record.update_challenge_history(current_player, previous_player, valid_challenge=False)
		current_player.lose_a_die(player_list)
