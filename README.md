# Analyzing the Effect of Turn Order on Liar’s Dice under Complex Player Behavior
## Overview
This project analyzes the effect of player turn order in the game liar’s dice under non-random player behavior.

Liar's dice is a game where players secretly roll dice and make bids on the total number of dice in play, both the known ones in a player's hand and those concealed in other players' hands. Bidding increases until a player challenges the previous bid by calling 'liar.' All players reveal the dice they rolled, and if the current bid is not in play, the previous player loses the round; if those dice are in play, the player who made the challenge loses the round.

[Previous work by Lin & Liang](https://github.com/Yena830/Liars_dice_IS597PR) showed that player order had a strong effect on win probabilities. 
Their First Caller Advantage experiment found that in a five-player game, the person to go last in the round actually has the greatest advantage, 
with the first player generally placing second overall. However, this experiment was only tested using random player behavior, not with the more 
advanced strategies (Preferred Dice Bid, Optimal Challenge Threshold, Conservative Bid Increase, etc.) developed later in that project. This 
project seeks to refine and expand upon those strategies and reanalyze the effect of player position with more complex, human-like player behaviors.

---
## Gameplay
1. **Roll:** All players secretly roll dice, with each player only looking at their own hand of dice.
2. **Opening bid:** The first player makes a bid on how many of a particular die face they believe are in play among all players' hands.
   - "I believe there are seven 4s."
3. **Bidding continues:** Subsequent players may make a new bid, but must increase the die face, the die quantity, or both. If increasing the 
   quantity of a bid, the player may bid for any die face, but the quantity can never decrease.
   - "There are seven 5s."
   - "Nine 4s."
   - "Eight 1s."
4. **Challenge:** Instead of making a new bid, a player can instead challenge the previous player by calling "Liar!"
5. **Reveal dice:** Players total up the number of dice in play and validate the challenge. The challenge fails if there are at least as many of 
   the chosen face in play as the challenged bid; the challenge succeeds if the challenged bid is higher than what's in play. The player that lost 
   the challenge is out of the game.
6. **New round begins:** Players reroll their dice and begin a new round. Play continues until only one player remains.

### Game Variations
- **Alternate Loss Penalty:** Instead of a player being immediately out of the game when they lose a challenge, they may instead lose one die but 
  continue to 
  play as long as they have dice to roll. This rule variation is necessary for some play strategies, and will be used after the validating the 
  model replicates the original project results.
- **Losing Player Bids First:** If a player loses a challenge, they make the first bid of the next round. This game variation will be explored 
  later in the project.

### Test Strategies
- **Logical Bidding:** Players prefer to make bids on the die face in their hand they have the most of, and increase the bid quantity by the lowest 
  amount possible. 
- **Optimal Challenge Threshold:** Players challenge a bid once the bid quantity is over a set percentage of the dice in play. Tests for different 
  challenge thresholds are required to find an optimal threshold value.
- **Preemptive Challenging:** If a player is about to make a bid that they themselves would challenge, it may prove advantageous to challenge the 
  previous player instead of making a risky bid themselves.
- **Situational Aggression:** Playing more aggressively or defensively as players lose dice may help take advantage of the unequal knowledge of the 
  game state. Players with more dice than their opponent can risk higher bids, and players with fewer dice could play more safely to avoid unsafe 
  challenges.

---
## Validation
TODO

---
## Player Strategies
### Logical Bidding
TODO

---
### Challenge Threshold 
TODO

---
### Preemptive Challenging 
TODO

---
### Situational Aggression
TODO

---
## Revisiting Turn Order Advantage
TODO

---
## Conclusion
TODO

## Limitations and Future Scope
TODO

---
## Library Dependencies
- IPython.display
- Matplotlib.pyplot
- Pandas
- Random

## References
Lin, Y., & Lian, J. (2024). Liars_dice_IS597PR. GitHub. https://github.com/Yena830/Liars_dice_IS597PR 