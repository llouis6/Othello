# this file contains the actual logic of my agent's playing, playing 8th out of 160 in a school
# programming competition


from agents.agent import Agent
from store import register_agent
import numpy as np
from copy import deepcopy
import time
from helpers import execute_move, get_valid_moves, get_directions, check_endgame
import sys

@register_agent("student_agent")
class StudentAgent(Agent):
  
  def __init__(self):
     super(StudentAgent, self).__init__()
     self.name = "StudentAgent"
     self.transposition_table = {} 

 # Find the best possible move and return it to be used later on 
  def step(self, chess_board, player, opponent):
      """
      Contains the search algorithm for finding the best move.
      Adjusts the search depth based on the board size.
      """
      start_time = time.time()
      time_limit = 1.95  # Slightly less than 2 seconds to be safe and make sure that none of our moves are exceedig the time limit

     # The board size changes so we are also going to want to determine the search depth based on how large the board is 
      N = chess_board.shape[0]
      # Adjust search depth based on board size
      if N <= 6:
          max_depth = 6
      elif N <= 8:
          max_depth = 5
      elif N <= 10:
          max_depth = 4
      else:
          max_depth = 3

      # Initialize best move
      best_move = None
      valid_moves = get_valid_moves(chess_board, player)

      if not valid_moves:
          return None  # Pass if no valid moves are available

      try:
          # Iterative deepening with move ordering
          for depth in range(1, max_depth + 1):
              if time.time() - start_time > time_limit:
                  raise TimeoutError()
              # Use shallow search to order moves
              ordered_moves = self.order_moves(chess_board, player, opponent, valid_moves)
              _, best_move = self.alpha_beta(chess_board, player, opponent, depth, -float('inf'), float('inf'), start_time, time_limit, ordered_moves)
      except TimeoutError:
          print(f"Time limit exceeded at depth {depth}. Using best move found so far.")

      if best_move is None:
          best_move = valid_moves[0]  # Fallback to the best move so far if timeout

      # Visualizing time taken per AI turn
      time_taken = time.time() - start_time
      print(f"My AI's turn took {time_taken:.4f} seconds.")

      return best_move

  def alpha_beta(self, board, player, opponent, depth, alpha, beta, start_time, time_limit, valid_moves):
      """
      Alpha-Beta pruning algorithm with move ordering and transposition table support.
      Optimizes the minimax algorithm by pruning branches that cannot influence the final decision.
      """
      # Check if time limit is exceeded to avoid timeout errors
      if time.time() - start_time > time_limit:
          raise TimeoutError()

      # Check the transposition table for previously computed results
      # If a deeper or equivalent depth has already been explored, reuse the stored value
      board_hash = self.hash_board(board, player)
      if board_hash in self.transposition_table and self.transposition_table[board_hash]['depth'] >= depth:
          return self.transposition_table[board_hash]['value'], None

      # Terminal condition: check for game-ending states or maximum search depth
      is_endgame, player_score, opponent_score = check_endgame(board, player, opponent)
      if depth == 0 or is_endgame:
          score = self.evaluate_board(board, player, opponent)
          return score, None

      max_score = -float('inf')  # Initialize the best score as negative infinity for maximizer
      best_move = None           # Initialize the best move as None

      for move in valid_moves:
          # Check for time limit within each move iteration to avoid timeout mid-calculation
          if time.time() - start_time > time_limit:
              raise TimeoutError()

          # Simulate the move and evaluate the resulting board state
          new_board = deepcopy(board)
          execute_move(new_board, move, player)
          new_valid_moves = get_valid_moves(new_board, opponent)

          # Recursive call: switch roles of player and opponent and decrease search depth
          score, _ = self.alpha_beta(new_board, opponent, player, depth - 1, -beta, -alpha, start_time, time_limit, new_valid_moves)
          score = -score  # Negate score since roles are reversed (minimizer for opponent)

          # Update the maximum score and best move if this move is better
          if score > max_score:
              max_score = score
              best_move = move

          # Update alpha and check for beta cutoff (pruning unpromising branches)
          alpha = max(alpha, max_score)
          if alpha >= beta:
              break  # Beta cutoff: no need to explore further moves

      # Store the computed result in the transposition table to avoid recomputation
      self.transposition_table[board_hash] = {'value': max_score, 'depth': depth}

      return max_score, best_move

  def order_moves(self, board, player, opponent, valid_moves):
      """
      Orders moves using a shallow evaluation to improve alpha-beta pruning efficiency.
      Better ordering can lead to faster pruning by prioritizing promising moves first.
      """
      move_scores = []
      for move in valid_moves:
          # Simulate the move and evaluate the resulting board
          new_board = deepcopy(board)
          execute_move(new_board, move, player)
          score = self.evaluate_board(new_board, player, opponent)
          move_scores.append((score, move))

      # Sort moves by score in descending order to maximize pruning opportunities
      move_scores.sort(reverse=True)
      ordered_moves = [move for _, move in move_scores]
      return ordered_moves

  def evaluate_board(self, board, player, opponent):
      """
      Evaluates the board state using a pattern-based heuristic function.
      Combines various strategic factors such as corners, edges, mobility, stability, and frontier discs.
      """
      WIN_BONUS = 1000000  # Large constant for rewarding terminal states

      # Calculate possible moves for both players to evaluate mobility
      my_moves = get_valid_moves(board, player)
      opp_moves = get_valid_moves(board, opponent)

      # If no valid moves remain, evaluate based on disk count as the game is effectively over
      if not my_moves and not opp_moves:
          my_disks = np.sum(board == player)
          opp_disks = np.sum(board == opponent)
          score = (my_disks - opp_disks) * WIN_BONUS
          return score

      # Define weights for different factors influencing the evaluation
      corner_weight = 25
      corner_adjacent_weight = -12.5
      edge_weight = 5
      mobility_weight = 10
      stability_weight = 8
      frontier_weight = -5

      N = board.shape[0]  # Board size (assumes square board)
      score = 0  # Initialize the heuristic score

      # Corners: owning corners is highly advantageous
      corners = [(0, 0), (0, N - 1), (N - 1, 0), (N - 1, N - 1)]
      my_corners = sum([1 for r, c in corners if board[r, c] == player])
      opp_corners = sum([1 for r, c in corners if board[r, c] == opponent])
      score += corner_weight * (my_corners - opp_corners)

      # Positions adjacent to corners: these are risky as they allow opponent to capture corners
      adjacents = []
      for r, c in corners:
          adjacents.extend(self.get_adjacent_positions(r, c, N))
      my_adjacent = sum([1 for r, c in adjacents if board[r, c] == player])
      opp_adjacent = sum([1 for r, c in adjacents if board[r, c] == opponent])
      score += corner_adjacent_weight * (my_adjacent - opp_adjacent)

      # Edges: controlling edges provides stability and limits opponent options
      edges = self.get_edges(N)
      my_edges = sum([1 for r, c in edges if board[r, c] == player])
      opp_edges = sum([1 for r, c in edges if board[r, c] == opponent])
      score += edge_weight * (my_edges - opp_edges)

      # Mobility: prioritize positions with more valid moves
      score += mobility_weight * (len(my_moves) - len(opp_moves))

      # Stability: prioritize stable discs that cannot be flipped
      my_stable = self.count_stable_disks(board, player)
      opp_stable = self.count_stable_disks(board, opponent)
      score += stability_weight * (my_stable - opp_stable)

      # Frontier Discs: minimize frontier discs to reduce exposure to flips
      my_frontier = self.count_frontier_discs(board, player)
      opp_frontier = self.count_frontier_discs(board, opponent)
      score += frontier_weight * (my_frontier - opp_frontier)

      return score

  def get_adjacent_positions(self, r, c, N):
      """
      Get all valid positions adjacent to a given position (r, c) on an NxN board.
      """
      positions = []
      directions = get_directions()  # Get all 8 possible directions
      for dr, dc in directions:
          nr, nc = r + dr, c + dc
          if 0 <= nr < N and 0 <= nc < N:  # Ensure position is within bounds
              positions.append((nr, nc))
      return positions

  def get_edges(self, N):
      """
      Get all edge positions on the board excluding corners.
      Edge positions provide strategic control but are less critical than corners.
      """
      edges = []
      for i in range(1, N - 1):
          edges.append((0, i))            # Top edge
          edges.append((N - 1, i))        # Bottom edge
          edges.append((i, 0))            # Left edge
          edges.append((i, N - 1))        # Right edge
      return edges

  def count_stable_disks(self, board, player):
      """
      Counts the number of stable disks for a player.
      Stable disks cannot be flipped by the opponent under any circumstances.
      """
      N = board.shape[0]
      stable = np.zeros((N, N), dtype=bool)

      # Check stability starting from the corners
      directions = get_directions()
      corners = [(0, 0), (0, N - 1), (N - 1, 0), (N - 1, N - 1)]
      for r, c in corners:
          if board[r, c] == player:
              stable[r, c] = True
              # Expand stability from the corner
              queue = [(r, c)]
              while queue:
                  cr, cc = queue.pop()
                  for dr, dc in directions:
                      nr, nc = cr + dr, cc + dc
                      if 0 <= nr < N and 0 <= nc < N and not stable[nr, nc] and board[nr, nc] == player:
                          stable[nr, nc] = True
                          queue.append((nr, nc))

      return np.sum(stable)

  def count_frontier_discs(self, board, player):
      """
      Counts the number of frontier discs for a given player.
      Frontier discs are adjacent to at least one empty square and are vulnerable to flips.
      """
      N = board.shape[0]
      frontier_count = 0
      directions = get_directions()

      for r in range(N):
          for c in range(N):
              if board[r, c] == player:
                  # Check if the disc is adjacent to an empty square
                  for dr, dc in directions:
                      nr, nc = r + dr, c + dc
                      if 0 <= nr < N and 0 <= nc < N and board[nr, nc] == 0:
                          frontier_count += 1
                          break  # Stop checking other directions for this disc
      return frontier_count

  def hash_board(self, board, player):
       #Creates a hashable representation of the board state for the transposition table.
        # Since bytes are hashable, we can use them directly in a tuple with the player
      """
      Creates a unique, hashable representation of the board state.
      Combines the board's binary representation and the current player.
      """
      board_bytes = board.tobytes()
      return (board_bytes, player)  # Use a tuple of board bytes and player as a unique key
