from classes import *


def generate_bid(this_player: AllPlayers, previous_bid: dict | None):
	"""
	
	Args:
		this_player:
		previous_bid:

	Returns:
	
	a_player = AllPlayers('Alpha', starting_hand_size=5, conservative_increase=True)
	AllPlayers.roll_dice()
	message = generate_bid(this_player=a_player, previous_bid={'Quantity': 6, 'Face': 6})
	print(message)
	
	"""
	
	total_dice = AllPlayers.total_dice
	
	# Get player's preferred faces and the quantity of them they have in hand
	highest_quantity = int(max(this_player.my_faces.values()))
	top_faces = sorted(a_face for a_face, count in this_player.my_faces.items() if count == highest_quantity)
	
	# First bid
	if previous_bid is None:
		if this_player.liar_threshold == -1: # Random behavior
			bid_quantity = random.randint(2, total_dice)
			face_value = random.randint(1, 6)
			return {'Quantity': bid_quantity, 'Face': face_value}
		
		# Use the smallest among the top face values
		# NOTE: Could select a random face in our hand so opponents don't know our top_faces immediately
		face_value = top_faces[0]
		
		# Bidding starts between the quantity of the face the player knows and expects to be in play
		average_quantity = total_dice // 6
		if average_quantity == 0:
			average_quantity = 1  # Prevents bidding 0 if the average_quantity is low
		
		bid_between = [highest_quantity, average_quantity]
		bid_quantity = random.randint(min(bid_between), max(bid_between))
		
		return {'Quantity': bid_quantity, 'Face': face_value}
	
	bid_quantity, bid_face = previous_bid.values()
	
	# Call "liar" if no further bids are possible
	if bid_quantity >= total_dice:
		return "Liar"
	
	if this_player.liar_threshold == -1:  # Random behavior
		bid_quantity = random.randint(bid_quantity+1, total_dice)
		possible_faces = [min(bid_face + 1, 6), 6]
		face_value = random.randint(min(possible_faces), max(possible_faces))
		return {'Quantity': bid_quantity, 'Face': face_value}
	
	# Attempts to increase the face using the same bid_quantity
	for this_face in top_faces:
		if this_face > bid_face:
			return {'Quantity': bid_quantity, 'Face': this_face}
	
	# Increase the bid_quantity using the smallest face from top_faces
	if this_player.conservative_increase:
		raised_quantity = min(bid_quantity + 1, total_dice)
	else:
		raised_quantity = random.randint(bid_quantity + 1, total_dice)
	return {'Quantity': raised_quantity, 'Face': top_faces[0]}


def generate_bid_endgame(this_player: AllPlayers, previous_bid: int | None):
	"""

	Args:
		this_player:
		previous_bid:

	Returns:

	a_player = AllPlayers('Alpha', starting_hand_size=5, conservative_increase=True)
	AllPlayers.roll_dice()
	message = generate_bid(this_player=a_player, previous_bid={'Quantity': 6, 'Face': 6})
	print(message)

	"""
	# TODO: Return bid risk
	own_roll = this_player.my_roll[0]
	
	if previous_bid == 12:
		return 'Liar'
	
	# First bid
	if previous_bid is None:
		previous_bid = 1
	
	if this_player.liar_threshold == -1: # Random behavior
		return random.randint(previous_bid + 1, 12)
	
	if previous_bid < own_roll:
		new_bid = random.randint(previous_bid + 1, own_roll + 1)
	else:
		new_bid = previous_bid + 1
	return new_bid


def consider_challenging(current_player: AllPlayers, opponents_bid, own_bid, endgame=False):
	# Cannot challenge before a bid is made
	if opponents_bid is None:
		return own_bid
	
	# Must challenge if the bid cannot be increased
	if own_bid == 'Liar':
		return 'Liar'
	
	# Random challenge threshold
	if current_player.liar_threshold == -1:
		return random.choice([own_bid, 'Liar'])
	
	if not endgame:
		opponents_quantity, opponents_face = opponents_bid.values()
		own_roll = current_player.my_faces
		unknown_dice_count = AllPlayers.total_dice - current_player.hand_size
		
		# Determine how many dice of opponents_face would have to be in other players' hands for bid to be true
		opponents_quantity = opponents_quantity - own_roll[opponents_face]
		
		# Determine the expected average of each die face in other players' hands
		expected_quantity = unknown_dice_count // 6
		
		# Challenge if opponent's bid is higher than the expected average
		if opponents_quantity > expected_quantity:
			return 'Liar'
		else:
			return own_bid
	else:
		own_roll = current_player.my_roll[0]
		# Challenge if opponent's bid is higher than the expected average
		if opponents_bid - own_roll > 3.5:
			return 'Liar'
		else:
			return own_bid


def call_liar(challenged_bid, previous_player, current_player, player_list: list):
	if isinstance(challenged_bid, dict):
		bid_quantity, bid_face = challenged_bid.values()
		dice_in_play = AllPlayers.total_faces
		
		# Challenge succeeds; the bid was a lie
		if bid_quantity > dice_in_play[bid_face]:
			challenge_result = 'Liar!'
		# Challenge fails; the bid was valid
		else:
			challenge_result = 'Challenge fails'
	
	# Endgame rules
	else:
		dice_sum = previous_player.my_roll[0] + current_player.my_roll[0]
		
		# Challenge succeeds; the bid was a lie
		if challenged_bid > dice_sum:
			challenge_result = 'Liar!'
		# Challenge fails; the bid was valid
		else:
			challenge_result = 'Challenge fails'
	
	if challenge_result == 'Liar!':
		Record.challenge(current_player, previous_player, valid_challenge=True)
		return previous_player.lose_a_die(player_list)
	else:
		Record.challenge(current_player, previous_player, valid_challenge=False)
		return current_player.lose_a_die(player_list)


if __name__ == '__main__':
	a_player = AllPlayers('Alpha', starting_hand_size=5, conservative_increase=True)
	b_player = AllPlayers('Bravo', starting_hand_size=5, conservative_increase=True)
	AllPlayers.roll_dice([a_player, b_player])
	message = call_liar({'Quantity': 2, 'Face': 6}, a_player, b_player, [a_player, b_player])
	print(message)
