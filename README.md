# Reversi/Othello AI Competition Platform

A Python framework for developing and testing AI agents in the classic board game Reversi/Othello. This project implements the complete game logic with an extensible agent system, allowing developers to create and test their own AI strategies.

> **Project Structure:** Inspired by David Meger's original work, enhanced for competitive AI development and a programming tournament.

## Report
[Othello AI Report (PDF)](Othello_report.pdf)

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Running Your First Game

Watch two random agents compete:

```bash
python simulator.py --player_1 random_agent --player_2 random_agent
```

## Game Modes

### Visual Games
Watch AI agents compete with board visualization:

```bash
python simulator.py --player_1 random_agent --player_2 random_agent --display
```

**Note:** Adjust the visualization speed with `--display_delay`:
```bash
python simulator.py --player_1 random_agent --player_2 random_agent --display --display_delay 0.5
```

### Human vs AI
Take control and test your skills against AI opponents:

```bash
python simulator.py --player_1 human_agent --player_2 random_agent --display
```

### Automated Tournaments
Run statistical battles to determine performance:

```bash
python simulator.py --player_1 random_agent --player_2 random_agent --autoplay --autoplay_runs 100
```

**Key Features:**
- Randomized board sizes (6x6 to 12x12) for robust testing
- Alternating player positions for fairness
- Aggregate win percentages for definitive results
- Automatic display disabled for speed

> **Note:** Only agents with `self.autoplay = True` can participate in tournaments (human agents excluded).

## Developing Your Own AI Agent

### Getting Started
1. Edit [`agents/student_agent.py`](agents/student_agent.py)
2. Extend the [`Agent`](agents/agent.py) base class
3. Implement the `step()` function with your strategy
4. Use helper functions from `helpers.py` (no additional imports needed)

### Testing Your Agent
```bash
# Test against random agent
python simulator.py --player_1 student_agent --player_2 random_agent --autoplay

# Challenge your own human play
python simulator.py --player_1 human_agent --player_2 student_agent --display
```

> **Performance Goal:** Consistently beating your own human gameplay indicates strong performance.

## Advanced Development

### Creating Multiple Agent Variants

To test different strategies, create additional agents:

1. **Copy** the base agent:
   ```bash
   cp agents/student_agent.py agents/second_agent.py
   ```

2. **Update** the decorator and class name:
   ```python
   @register_agent("second_agent")
   class SecondAgent(Agent):
   ```

3. **Register** in [`agents/__init__.py`](agents/__init__.py):
   ```python
   from .second_agent import SecondAgent
   ```

4. **Test** your agents:
   ```bash
   python simulator.py --player_1 student_agent --player_2 second_agent --display
   ```

### Development Guidelines

- **DO:** Use helper functions from `helpers.py`
- **DO:** Add custom logic as global/class variables
- **DON'T:** Import `world.py`
- **DON'T:** Add external imports to `student_agent.py`

## Complete API Reference

```bash
python simulator.py --help
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--player_1` | First agent to play | - |
| `--player_2` | Second agent to play | - |
| `--board_size` | Fixed board size | Random (6-12) |
| `--display` | Enable visual mode | False |
| `--display_delay` | Delay between moves (seconds) | 1.0 |
| `--autoplay` | Run automated tournament | False |
| `--autoplay_runs` | Number of games to run | 10 |
| `--board_size_min` | Minimum board size for autoplay | 6 |
| `--board_size_max` | Maximum board size for autoplay | 12 |

### Available Agents

- `random_agent` - Random move selection
- `human_agent` - Human player input
- `student_agent` - Your custom implementation
- *Additional agents as you create them*

## Strategy Approaches

### Beginner Strategies
- **Random:** Start with random moves to understand the game
- **Greedy:** Always take the move that captures the most pieces
- **Positional:** Focus on corner and edge control

### Advanced Techniques
- **Minimax:** Look ahead multiple moves
- **Alpha-Beta Pruning:** Optimize minimax performance
- **Monte Carlo:** Simulate random game completions
- **Machine Learning:** Train neural networks on game positions

## Contributing

This platform is designed for educational and competitive AI development. Contributions welcome:
- Create new agent implementations
- Improve the visualization system
- Add new game variants
- Share your strategies

---

**Happy coding and may the best AI win!**
