## Qt-based UI Engine
import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPalette
import numpy as np
from constants import PLAYER_1_COLOR, PLAYER_2_COLOR, PLAYER_1_NAME, PLAYER_2_NAME


# Headless safety for Linux
if sys.platform == "linux" and not os.environ.get("DISPLAY"):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"


class OthelloWidget(QWidget):
    """Custom widget that draws the Othello board"""
    
    def __init__(self, grid_size, world):
        super().__init__()
        self.grid_size = grid_size
        self.world = world
        self.chess_board = None
        self.debug = False
        
        # Visual constants
        self.cell_size = 60
        self.margin = 40
        self.header_height = 80
        self.footer_height = 80
        
        # Calculate window size
        board_width = self.cell_size * grid_size
        board_height = self.cell_size * grid_size
        total_width = board_width + 2 * self.margin
        total_height = board_height + self.header_height + self.footer_height
        
        self.setFixedSize(total_width, total_height)
        
        # Color mapping
        self.color_map = {
            "tab:blue": QColor(31, 119, 180),
            "tab:brown": QColor(140, 86, 75)
        }
    
    def update_board(self, chess_board, debug=False):
        """Update the board state and trigger repaint"""
        self.chess_board = chess_board
        self.debug = debug
        self.update()  # Trigger paintEvent
    
    def paintEvent(self, event):
        """Main rendering method"""
        if self.chess_board is None:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(11, 15, 20))
        
        # Draw board panel
        self._draw_board_panel(painter)
        
        # Draw grid and pieces
        self._draw_grid_and_pieces(painter)
        
        # Draw text info
        self._draw_text_info(painter)
    
    def _draw_board_panel(self, painter):
        """Draw the board background panel"""
        board_x = self.margin
        board_y = self.header_height
        board_width = self.cell_size * self.grid_size
        board_height = self.cell_size * self.grid_size
        
        # Board background
        painter.setBrush(QBrush(QColor(30, 35, 40)))
        painter.setPen(QPen(QColor(60, 65, 70), 2))
        painter.drawRoundedRect(board_x - 10, board_y - 10, 
                               board_width + 20, board_height + 20, 8, 8)
    
    def _draw_grid_and_pieces(self, painter):
        """Draw grid lines and game pieces"""
        board_x = self.margin
        board_y = self.header_height
        
        # Draw grid lines
        painter.setPen(QPen(QColor(80, 85, 90), 1))
        for i in range(self.grid_size + 1):
            # Vertical lines
            x = board_x + i * self.cell_size
            painter.drawLine(x, board_y, x, board_y + self.cell_size * self.grid_size)
            # Horizontal lines
            y = board_y + i * self.cell_size
            painter.drawLine(board_x, y, board_x + self.cell_size * self.grid_size, y)
        
        # Draw pieces
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell_value = self.chess_board[row][col]
                if cell_value != 0:
                    self._draw_disc(painter, row, col, cell_value, board_x, board_y)
                
                # Debug coordinates
                if self.debug:
                    self._draw_debug_coords(painter, row, col, board_x, board_y)
    
    def _draw_disc(self, painter, row, col, player, board_x, board_y):
        """Draw a game disc"""
        center_x = board_x + col * self.cell_size + self.cell_size / 2
        center_y = board_y + row * self.cell_size + self.cell_size / 2
        radius = self.cell_size / 2.5
        
        # Choose color
        if player == 1:
            color = self.color_map[PLAYER_1_COLOR]
        else:
            color = self.color_map[PLAYER_2_COLOR]
        
        # Draw disc with subtle outline
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color.darker(120), 2))
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)
        
        # Very subtle highlight
        highlight_offset = radius * 0.3
        highlight_radius = radius * 0.2
        painter.setBrush(QBrush(QColor(255, 255, 255, 40)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(center_x - highlight_offset, center_y - highlight_offset), 
                           highlight_radius, highlight_radius)
    
    def _draw_debug_coords(self, painter, row, col, board_x, board_y):
        """Draw debug coordinates"""
        center_x = board_x + col * self.cell_size + self.cell_size / 2
        center_y = board_y + row * self.cell_size + self.cell_size / 2
        
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("Arial", 8))
        painter.drawText(QRectF(center_x - 15, center_y - 10, 30, 20), 
                        Qt.AlignCenter, f"{row},{col}")
    
    def _draw_text_info(self, painter):
        """Draw player info and scores"""
        # Player names and current turn indicator
        turn = 1 - self.world.turn
        
        # Player 1 info (left side)
        painter.setFont(QFont("Arial", 14, QFont.Bold if turn == 0 else QFont.Normal))
        painter.setPen(QPen(self.color_map[PLAYER_1_COLOR]))
        agent_0_text = f"{PLAYER_1_NAME}: {self.world.p0}"
        painter.drawText(20, 30, agent_0_text)
        
        # Player 2 info (left side, below player 1)
        painter.setFont(QFont("Arial", 14, QFont.Bold if turn == 1 else QFont.Normal))
        painter.setPen(QPen(self.color_map[PLAYER_2_COLOR]))
        agent_1_text = f"{PLAYER_2_NAME}: {self.world.p1}"
        painter.drawText(20, 55, agent_1_text)
        
        # Scores (if game has results)
        if len(self.world.results_cache) > 0:
            painter.setFont(QFont("Arial", 13))
            painter.setPen(QPen(QColor(200, 200, 200)))
            
            score_text = f"Scores: Blue: [{self.world.results_cache[1]}], Brown: [{self.world.results_cache[2]}]"
            footer_y = self.height() - 50
            painter.drawText(20, footer_y, score_text)
            
            # Win message
            if self.world.results_cache[0]:
                if self.world.results_cache[1] > self.world.results_cache[2]:
                    win_text = "Blue wins!"
                elif self.world.results_cache[1] < self.world.results_cache[2]:
                    win_text = "Brown wins!"
                else:
                    win_text = "It is a Tie!"
                
                painter.setFont(QFont("Arial", 16, QFont.Bold))
                painter.setPen(QPen(QColor(100, 255, 100)))
                painter.drawText(20, footer_y + 25, win_text)


class UIEngine:
    """Qt-based UI Engine - API-compatible with matplotlib version"""
    
    def __init__(self, grid_width=5, world=None):
        self.grid_size = (grid_width, grid_width)
        self.world = world
        self.step_number = 0
        
        # Initialize Qt application (safe if already exists)
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        
        # Create and show window
        self.widget = OthelloWidget(grid_width, world)
        self.widget.setWindowTitle("Othello/Reversi")
        self.widget.show()
        
        # Process initial events
        self.app.processEvents()
    
    def render(self, chess_board, debug=False):
        """Main render method - preserves exact API"""
        # Update board state
        self.widget.update_board(chess_board, debug)
        
        # Process Qt events (equivalent to plt.pause)
        self.app.processEvents()
        
        # Handle frame saving
        if self.world.display_save:
            self._save_frame()
        
        self.step_number += 1
    
    def _save_frame(self):
        """Save current frame as PNG"""
        Path(self.world.display_save_path).mkdir(parents=True, exist_ok=True)
        filename = f"{self.world.display_save_path}/{self.world.player_1_name}_{self.world.player_2_name}_{self.step_number}.png"
        pixmap = self.widget.grab()
        pixmap.save(filename)


if __name__ == "__main__":
    # Simple test
    app = QApplication(sys.argv)
    
    class MockWorld:
        def __init__(self):
            self.turn = 0
            self.p0 = "TestAgent1"
            self.p1 = "TestAgent2"
            self.results_cache = ()
            self.display_save = False
    
    world = MockWorld()
    engine = UIEngine(8, world)
    
    # Create test board
    chess_board = np.zeros((8, 8), dtype=int)
    chess_board[3][3] = 2
    chess_board[3][4] = 1
    chess_board[4][3] = 1
    chess_board[4][4] = 2
    
    engine.render(chess_board)
    app.exec()
