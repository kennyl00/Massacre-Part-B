-------------
Introduction
-------------
Before starting the project, we first separated out our task into four separate
Phases. The 1st Phase details the implementation of the Player class as well
as the Game itself. This also includes facilitating the communications between
the Referee and the Player as it was initially intended by the Head Tutor.
The 2nd Phase narrows down on the second part of the game, which was the
moving phase. This Phase also includes the implementation of the Minimax
algorithm with alpha and beta pruning in order to allow game playing agent to
look five moves ahead. The 3rd Phase covers the data collection from the game
playing agent through our ad hoc Linear Regression functions. The 4th Phase
focuses on the placing phase. This includes our take on the Monte Carlo Tree
Search algorithm.

---------------------------------------------
The 1st Phase: Setting Up the Player Class
---------------------------------------------
Before we started the designing the Player class, we had to make a decision as
to whether we should reuse our own take on the Game from Part A or reuse the
code that was written by the Head Tutor. Given that our initial design from
Part A had failed a test case and the late release of said test case from the
Head Tutor, we decided that it was a safer option to use the Game that was set
up by the Head Tutor.

After we had fully understood how our Head Tutor had designed the game, we set
up the Player class accordingly. We made sure that the Player class was able to
communicate freely with the Referee. There were some functions that needed to be
improvised, however this Phase overall was completed with ease.

------------------------------------------
The 2nd Phase: Moving and the Minimax
------------------------------------------
After setting up the game playing mechanisms, we focused on the moving phase. We
implemented the Minimax algorithm with alpha-beta pruning. The algorithm goes
into a max depth of 5, which is an estimation of 3 moves of self player and 2
moves of the other player. We initialised the alpha to be negative infinity and
tried to obtain the highest alpha in the search. We can then determined the most
optimal move.

Using the Minimax algorithm, we decided the next move of the game playing agent.
We then shuffle the list of the pieces that resides on the board. This is to
avoid extreme conditions like the most optimal piece being placed at the very
end of the list. If this had occurred, the alpha-beta pruning will not improve
the search speed at all. Since the search speed is already extremely slow, by
not shuffling, the time taken for each turn could result in a time out. We had
considered the option to sort the pieces in the list to make the alpha-beta
pruning more efficient, however we later realised that this would take up a lot
of time. Hence, as a result, we have decided to shuffle instead.

Our Evaluation function was designed so that the difference between the enemy’s
pieces and our pieces would be multiplied by a Weight of 100. This weight number
was chosen arbitrarily and has no significant bearings.

In addition to this, we have implemented a Step attribute in response to the
Shrink event that occurs periodically on the Board. After the completion of the
Minimax algorithm, we had stimulated different games with random placings at the
start and we noticed that the Shrinking event had an enormous pull on the
outcome of the game. Hence, in order to make Player to be fully aware of the
zones that were going to be eliminated due to the Shrinking event, we had to
take them into account within the Heuristics function. We designed the Step
function as such:

self.step = round(self.turns*(pow(2, self.shrink_num)*self.initial_step),2)

The goal of the Step is to outweigh the elimination of the enemy pieces in the
Hot Spots (Shrink zones that eliminates pieces) in order to prevent our own
pieces from being eliminated. Hence, as turns goes by the Player would find more
and more incentive to move out of the Hot Spots instead of staying in. We
decided to use an initial Step that would be multiplied by the number of
turns. When the Shrink event occurs, the Step attribute would reset to 0. This
is followed by the increment of the step increasing 2 folds, since the time
taken for the next Shrink event to occur has been halved.

---------------------------------------------------------------
The 3rd Phase: Determining the Steps with Linear Regression
---------------------------------------------------------------
From the Second Phase, we mentioned that we have implemented a Weight of 100
for the Heuristic function. This random number that we have chosen became a
standard that we have to abide by. For instance, the Step attribute now has to
compliment the Weight standard. We however do not know what the initial Step
value should be.

We can theorise, that since it takes a Player 64 turns before the First Shrink,
and the Weight of eliminating 1 enemy Piece cost 100 points, if we want to save
another Piece of our own from a Hot Spot we would want the step to accrued to
exactly 100 points at turn 64. This makes out to a Step value of 0.64.

To put this to a test, we incorporated an ad hoc Linear Regression function.
The Player would play random games (placing is random) under different Step
values from 0.60 to 0.69. All of which totalling up to a 1000 games (each 100).
We then record the results (Wins/ Losses) in a data.txt file. We then used
Numpy framework to calculate and plot the results that we have taken. We
hypothesised that by increasing the value we would see a positive relationship
between the Steps and the Win-rate. The results showed otherwise. There were
high win rates across the board.

Not capturing what we intended to, we decided to double down. We played random
games up to 1000 times in total with a Step variation from 1 to 2, within a 2
decimal range. Using Numpy, we then plotted the results to see if there was any
correlation between increasing the size of the Steps and the Win rate.
Unfortunately, the graph (located in old data) didn’t yield meaningful data.
It shows a positive trend across the board, however the win rates were scattered
all over. We just didn’t have enough data.

We had intended to use our data from the data.txt file to calculate the best
Step that a Player should use for their next game. And whenever it loses or
wins, it would record the results. Hence, the game playing agent would learn
after every game. But our plan had one particular downfall. Judging from our
past data collection, we are not confident that our game playing agent has
sufficient data to extract from, in order to yield a high win rate Step value
when against another Player.

This uncertainty largely stems from our games, the models that we had our data
collected from. We are not sure as to whether we have fully understood all of
the variables at work when collecting the data. Our model involves 2 Player of
the same kind versing each other. The placing phase would be randomised. The
White Player would use a Step value from a range of 0.60 to 0.69 while the
Black Player would use a step value of 0. And vice versa.

----------------------------------------------
The 4th Phase: The Monte Carlo Tree Search
----------------------------------------------
Lastly, for our placing phase we decided to use a Monte Carlo Tree Search.
Since the initial starting phase mimics the game Go, and we have heard of the
use of MCTS in AlphaGo, we decided to give it incorporate it in our project.
Not to mention that MCTS cost less space than Minimax. This is crucial as there
could be up to 64 opening moves (the entire board).

The Monte Carlo Tree Search is different from Minimax, as it takes in the
current Board State and run random simulations for a given time. When the
simulation is done, it would update the current Board State with the number of
wins and plays. Hence, it would return a next move that yields that highest win
ratio. The Tree however is governed by UCB1 algorithm that determines
whether the current Board State should be investigated further or we should
explore other moves. The constant that toggles between the exploration and
exploitation is referred to as the constant C. Given the same time, the higher
the C value is, the more exploration of different moves, but the less
exploitation of a selected move. And vice versa.

Given that our time limit is 120 seconds, we have decided to leave 2 seconds
for the stimulations to occur. Given that we want to explore as many moves as
possible, we increased the constant C to a value of 5, which guarantees at
least a visit to every different moves currently available. However, the
simulations might not be as extensive as it could be. Since there are
constraints, we didn’t want to push our limits.

While implementing the MCTS, we discovered that it wouldn’t visit a move that
would lead to the elimination of an enemy piece, regardless of the position.
This was critical, as the outcome of the game is usually heavily influenced by
the placing phase. Losing the opportunity to eliminate enemy pieces, would
severely increase our chances of losing the game. Hence, we decided to patch it
up by bypassing the MCTS if there were any pieces that could be eliminated on
the board. Consequently, this lead to many unforeseeable behaviours that would
not be characterised as smart. However, we decided that the elimination of enemy
pieces takes precedent at the placing phase oppose to finding a better move to
set up on the board.

There were still so many other variables that we could collect data on with
Machine Learning to yield the best results. For instance, the constant C and
the time run for a stimulation. However due to the limited amount of time that
we had, we were unable to do so.

-----------
Conclusion
-----------
Although this project was a moderate task for a team of two, we were not fully
prepared for what was about to hit us. Primarily, there were simply too many
occurrence where we have to rely our own intuition as to how to set up the model
in order to yield meaningful data. Under the creative section, the team had
decided to implement a simple Machine Learning technique in order to facilitate
our game playing agent. Setting up the infrastructure was not a complicated
issue, the difficulty however lies in the data collection itself. We just didn’t
know how to collect the right data.

There were just too many variables that we didn’t even consider at the start.
With trial and error methods, and home-brewed functionalities that we had
implemented in order to make it work, our results were simply filled with white
noises. There was simply no definitive relationship that we could have
established. Not to mention, because we have decided to implement algorithmic
techniques that was not covered in our curriculum, our game playing agent took a
hit on its own structural integrity. This turned our somewhat moderate task into
a colossal mess at a really quick pace.

Despite the pessimistic overview, our game playing agent fulfils its required
task, and displays a magnitude of competency in terms of developing its own
strategies in order to win. However it still falls short on our own expectations
when we first started out. We have learned a lot, and we mean a lot from our
mistakes (collecting data) and that we would definitely look out for it in the
future.
