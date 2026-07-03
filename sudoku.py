#!/usr/bin/env python3
"""
Sudoku Game with 10 Difficulty Levels
=====================================
A CLI-based Sudoku game with customizable difficulty levels.

Features:
- 10 difficulty levels (Very Easy to Extreme)
- Random puzzle generation
- Input validation
- Timer
- Mistake counter
- Hint system
- Save/Load game state

Usage:
    python sudoku.py [difficulty]
    
Example:
    python sudoku.py 5  # Starts a game with difficulty level 5 (Medium)
"""

import random
import time
import copy
import os
import sys
import json
from typing import List, Tuple, Optional, Dict, Any


# Difficulty levels (1-10)
DIFFICULTY_LEVELS = {
    1: "Very Easy",
    2: "Easy",
    3: "Beginner",
    4: "Intermediate",
    5: "Medium",
    6: "Hard",
    7: "Challenging",
    8: "Expert",
    9: "Master",
    10: "Extreme",
}

# Number of cells to remove for each difficulty (higher = harder)
DIFFICULTY_CELLS_REMOVED = {
    1: 30,   # Very Easy
    2: 35,   # Easy
    3: 40,   # Beginner
    4: 45,   # Intermediate
    5: 50,   # Medium
    6: 55,   # Hard
    7: 58,   # Challenging
    8: 60,   # Expert
    9: 62,   # Master
    10: 64,  # Extreme
}


class SudokuGame:
    """Main Sudoku game class."""
    
    def __init__(self, difficulty: int = 5):
        """
        Initialize a new Sudoku game.
        
        Args:
            difficulty: Difficulty level (1-10)
        """
        if difficulty < 1 or difficulty > 10:
            raise ValueError("Difficulty must be between 1 and 10")
        
        self.difficulty = difficulty
        self.difficulty_name = DIFFICULTY_LEVELS[difficulty]
        self.cells_removed = DIFFICULTY_CELLS_REMOVED[difficulty]
        
        # Generate a solved board
        self.solved_board = self._generate_solved_board()
        
        # Create the puzzle by removing cells
        self.board = self._generate_puzzle()
        
        # Initialize game state
        self.initial_board = copy.deepcopy(self.board)
        self.user_board = copy.deepcopy(self.board)
        self.start_time = None
        self.end_time = None
        self.mistakes = 0
        self.hints_used = 0
        
    def _generate_solved_board(self) -> List[List[int]]:
        """Generate a fully solved Sudoku board."""
        # Start with an empty board
        board = [[0 for _ in range(9)] for _ in range(9)]
        
        # Fill the diagonal boxes (they are independent)
        self._fill_diagonal_boxes(board)
        
        # Solve the rest of the board
        self._solve_board(board)
        
        return board
    
    def _fill_diagonal_boxes(self, board: List[List[int]]) -> None:
        """Fill the diagonal 3x3 boxes with valid numbers."""
        for box in range(0, 9, 3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            for i in range(3):
                for j in range(3):
                    board[box + i][box + j] = nums.pop()
    
    def _solve_board(self, board: List[List[int]]) -> bool:
        """Solve the Sudoku board using backtracking."""
        empty = self._find_empty_cell(board)
        if not empty:
            return True  # Puzzle solved
        
        row, col = empty
        
        for num in range(1, 10):
            if self._is_valid_move(board, row, col, num):
                board[row][col] = num
                
                if self._solve_board(board):
                    return True
                
                board[row][col] = 0  # Backtrack
        
        return False
    
    def _find_empty_cell(self, board: List[List[int]]) -> Optional[Tuple[int, int]]:
        """Find an empty cell (with value 0)."""
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return (i, j)
        return None
    
    def _is_valid_move(self, board: List[List[int]], row: int, col: int, num: int) -> bool:
        """Check if placing 'num' at (row, col) is valid."""
        # Check row
        if num in board[row]:
            return False
        
        # Check column
        if num in [board[i][col] for i in range(9)]:
            return False
        
        # Check 3x3 box
        box_row, box_col = row // 3 * 3, col // 3 * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if board[i][j] == num:
                    return False
        
        return True
    
    def _generate_puzzle(self) -> List[List[int]]:
        """Generate a puzzle by removing cells from the solved board."""
        puzzle = copy.deepcopy(self.solved_board)
        cells = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(cells)
        
        # Remove cells while ensuring the puzzle remains solvable
        cells_removed = 0
        for row, col in cells:
            if cells_removed >= self.cells_removed:
                break
            
            # Save the current value
            temp = puzzle[row][col]
            puzzle[row][col] = 0
            
            # Make a copy to test uniqueness
            puzzle_copy = copy.deepcopy(puzzle)
            
            # Count solutions
            solution_count = self._count_solutions(puzzle_copy)
            
            if solution_count == 1:
                cells_removed += 1
            else:
                puzzle[row][col] = temp  # Restore if not unique
        
        return puzzle
    
    def _count_solutions(self, board: List[List[int]], count: int = 0) -> int:
        """Count the number of solutions for a given board."""
        if count > 1:
            return count  # Early exit if we already have multiple solutions
        
        empty = self._find_empty_cell(board)
        if not empty:
            return count + 1
        
        row, col = empty
        
        for num in range(1, 10):
            if self._is_valid_move(board, row, col, num):
                board[row][col] = num
                count = self._count_solutions(board, count)
                board[row][col] = 0
                
                if count > 1:
                    return count
        
        return count
    
    def start(self) -> None:
        """Start the game."""
        self.start_time = time.time()
        print(f"\n{'='*50}")
        print(f"  SUDOKU - {self.difficulty_name.upper()} LEVEL ({self.difficulty}/10)")
        print(f"{'='*50}\n")
        print("Commands: row col num (e.g., '5 3 7'), 'hint', 'check', 'quit'")
        print(f"Cells to fill: {self.cells_removed}\n")
        self._display_board()
        
        while True:
            user_input = input("\nYour move (or command): ").strip().lower()
            
            if not user_input:
                continue
            
            if user_input == "quit":
                self._quit_game()
                break
            elif user_input == "hint":
                self._use_hint()
            elif user_input == "check":
                self._check_board()
            elif user_input == "solve":
                self._show_solution()
            elif user_input == "save":
                self._save_game()
            else:
                # Parse move: row col num
                parts = user_input.split()
                if len(parts) == 3:
                    try:
                        row = int(parts[0]) - 1
                        col = int(parts[1]) - 1
                        num = int(parts[2])
                        
                        if 0 <= row < 9 and 0 <= col < 9 and 1 <= num <= 9:
                            self._make_move(row, col, num)
                        else:
                            print("Invalid input. Row and column must be 1-9, number must be 1-9.")
                    except ValueError:
                        print("Invalid input. Please enter: row col num (e.g., '5 3 7')")
                else:
                    print("Invalid input. Please enter: row col num (e.g., '5 3 7') or a command.")
    
    def _make_move(self, row: int, col: int, num: int) -> None:
        """Make a move on the board."""
        # Check if the cell is modifiable (not part of the initial puzzle)
        if self.initial_board[row][col] != 0:
            print(f"Cell ({row+1},{col+1}) is part of the puzzle and cannot be changed.")
            return
        
        # Check if the move is valid
        if self._is_valid_move(self.user_board, row, col, num):
            self.user_board[row][col] = num
            
            # Check if the board is solved
            if self._is_board_solved():
                self._win_game()
        else:
            self.mistakes += 1
            print(f"Invalid move! That's mistake #{self.mistakes}")
        
        self._display_board()
    
    def _is_board_solved(self) -> bool:
        """Check if the board is solved correctly."""
        for i in range(9):
            for j in range(9):
                if self.user_board[i][j] != self.solved_board[i][j]:
                    return False
        return True
    
    def _use_hint(self) -> None:
        """Reveal a correct number for an empty cell."""
        # Find all empty cells that the user can fill
        empty_cells = []
        for i in range(9):
            for j in range(9):
                if self.initial_board[i][j] == 0 and self.user_board[i][j] == 0:
                    empty_cells.append((i, j))
        
        if not empty_cells:
            print("No empty cells left to hint!")
            return
        
        # Choose a random empty cell
        row, col = random.choice(empty_cells)
        correct_num = self.solved_board[row][col]
        self.user_board[row][col] = correct_num
        self.hints_used += 1
        
        print(f"\nHint used! Cell ({row+1},{col+1}) is {correct_num}")
        print(f"Total hints used: {self.hints_used}")
        self._display_board()
    
    def _check_board(self) -> None:
        """Check the current board for errors."""
        errors = []
        for i in range(9):
            for j in range(9):
                if self.user_board[i][j] != 0 and self.user_board[i][j] != self.solved_board[i][j]:
                    errors.append((i, j, self.user_board[i][j]))
        
        if not errors:
            print("\n✓ Board is correct so far!")
        else:
            print(f"\n✗ Found {len(errors)} error(s):")
            for row, col, num in errors[:5]:  # Show first 5 errors
                print(f"  Cell ({row+1},{col+1}): {num} (should be {self.solved_board[row][col]})")
            if len(errors) > 5:
                print(f"  ... and {len(errors) - 5} more")
    
    def _show_solution(self) -> None:
        """Show the complete solution."""
        print("\n" + "="*50)
        print("  SOLUTION")
        print("="*50)
        self._display_board(self.solved_board)
        print("="*50)
    
    def _quit_game(self) -> None:
        """Quit the game and show statistics."""
        self.end_time = time.time()
        elapsed = self.end_time - self.start_time
        
        print("\n" + "="*50)
        print("  GAME OVER")
        print("="*50)
        print(f"Difficulty: {self.difficulty_name} ({self.difficulty}/10)")
        print(f"Time played: {elapsed:.2f} seconds")
        print(f"Mistakes: {self.mistakes}")
        print(f"Hints used: {self.hints_used}")
        
        if self._is_board_solved():
            print("\n🎉 CONGRATULATIONS! You solved the puzzle!")
        else:
            print("\nBetter luck next time!")
        
        print("="*50)
    
    def _display_board(self, board: Optional[List[List[int]]] = None) -> None:
        """Display the current board state."""
        if board is None:
            board = self.user_board
        
        print("\n   " + " ".join(str(i) for i in range(1, 10)))
        print("  " + "-" * 19)
        
        for i, row in enumerate(board):
            print(f"{i+1} |", end=" ")
            for j, cell in enumerate(row):
                if cell == 0:
                    print(".", end=" ")
                else:
                    print(cell, end=" ")
                if (j + 1) % 3 == 0 and j < 8:
                    print("|", end=" ")
            print()
            if (i + 1) % 3 == 0 and i < 8:
                print("  " + "-" * 19)
    
    def _save_game(self) -> None:
        """Save the current game state to a file."""
        state = {
            "difficulty": self.difficulty,
            "board": self.board,
            "user_board": self.user_board,
            "initial_board": self.initial_board,
            "solved_board": self.solved_board,
            "start_time": self.start_time,
            "mistakes": self.mistakes,
            "hints_used": self.hints_used,
        }
        
        filename = f"sudoku_save_{int(time.time())}.json"
        with open(filename, "w") as f:
            json.dump(state, f)
        
        print(f"\nGame saved to {filename}")
    
    @classmethod
    def load_game(cls, filename: str) -> "SudokuGame":
        """Load a game from a file."""
        with open(filename, "r") as f:
            state = json.load(f)
        
        game = cls(state["difficulty"])
        game.board = state["board"]
        game.user_board = state["user_board"]
        game.initial_board = state["initial_board"]
        game.solved_board = state["solved_board"]
        game.start_time = state["start_time"]
        game.mistakes = state["mistakes"]
        game.hints_used = state["hints_used"]
        
        return game


def print_welcome():
    """Print the welcome message."""
    print("""
  ███████╗██╗   ██╗███╗   ██╗ ██████╗ ██████╗ ███████╗███████╗
  ██╔════╝╚██╗ ██╔╝████╗  ██║██╔═══██╗██╔══██╗██╔════╝██╔════╝
  █████╗   ╚████╔╝ ██╔██╗ ██║██║   ██║██████╔╝█████╗  ███████╗
  ██╔══╝    ╚██╔╝  ██║╚██╗██║██║   ██║██╔══██╗██╔══╝  ╚════██║
  ██║        ██║   ██║ ╚████║╚██████╔╝██║  ██║███████╗███████║
  ╚═╝        ╚═╝   ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝

  ███████╗██████╗  ██████╗ ██████╗ ██╗     ███████╗███████╗
  ██╔════╝██╔══██╗██╔═══██╗██╔══██╗██║     ██╔════╝██╔════╝
  █████╗  ██████╔╝██║   ██║██║  ██║██║     █████╗  ███████╗
  ██╔══╝  ██╔══██╗██║   ██║██║  ██║██║     ██╔══╝  ╚════██║
  ██║     ██║  ██║╚██████╔╝██████╔╝███████╗███████╗███████║
  ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝

    Welcome to Sudoku with 10 Difficulty Levels!
    """)
    
    print("Available Difficulty Levels:")
    for level, name in DIFFICULTY_LEVELS.items():
        print(f"  {level}. {name}")
    print()


def main():
    """Main function to run the Sudoku game."""
    print_welcome()
    
    # Get difficulty level from command line or user input
    difficulty = 5  # Default
    
    if len(sys.argv) > 1:
        try:
            difficulty = int(sys.argv[1])
            if difficulty < 1 or difficulty > 10:
                print("Difficulty must be between 1 and 10. Using default (5).")
                difficulty = 5
        except ValueError:
            print("Invalid difficulty. Using default (5).")
            difficulty = 5
    else:
        while True:
            try:
                difficulty = int(input("Enter difficulty level (1-10, default 5): ").strip() or "5")
                if 1 <= difficulty <= 10:
                    break
                else:
                    print("Please enter a number between 1 and 10.")
            except ValueError:
                print("Please enter a valid number.")
    
    print(f"\nStarting a new game with difficulty: {DIFFICULTY_LEVELS[difficulty]}")
    
    # Create and start the game
    game = SudokuGame(difficulty)
    game.start()


if __name__ == "__main__":
    main()
