"""
    this is the very basic implementation for the racing kings game,
    for now it only has one opponent piece to make it super easy.

    you can learn the game from chess.com
    https://www.chess.com/terms/racing-kings-chess,
    Ive used images from here:
    https://commons.wikimedia.org/wiki/Category:SVG_chess_pieces
"""
import pygame
import gymnasium as gym
import numpy as np


class RacingKingsEnv(gym.Env):
    def __init__(self):
        super().__init__()


        self.width = 8
        self.height = 8
        self.cell_size = 80
        
        self.reset()

        self.action_space = gym.spaces.Discrete(8)
        self.observation_space = gym.spaces.Box(low=-1, high=1, shape=(8, 8))
        

        # pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode((self.width * self.cell_size, self.height * self.cell_size))
        self.clock = pygame.time.Clock()

    def reset(self):
        self.board = np.full((self.width, self.height), 'E', dtype=str)
        self.board[7, 7] = 'K' # white king
        self.board[7, 2] = 'b'  # black bishop

        return self.board

    def step(self, action):

        # find the king position
        king_pos = np.where(self.board == 'K')
        self.king = king_pos

        if action == 1 and king_pos[1][0] - 1 >= 0:  # up
            self.board[king_pos[0][0], king_pos[1][0] - 1] = self.board[king_pos[0][0], king_pos[1][0]]
            self.board[king_pos[0][0], king_pos[1][0]] = 'E'
        if action == 2 and king_pos[0][0] - 1 >= 0:  # left
            self.board[king_pos[0][0] - 1, king_pos[1][0]] = self.board[king_pos[0][0], king_pos[1][0]]
            self.board[king_pos[0][0], king_pos[1][0]] = 'E'
        if action == 2 and king_pos[1][0] + 1 < self.height:  # bottom
            self.board[king_pos[0][0], king_pos[1][0] + 1] = self.board[king_pos[0][0], king_pos[1][0]]
            self.board[king_pos[0][0], king_pos[1][0]] = 'E'
        if action == 3 and king_pos[0][0] + 1 < self.width:  # right
            self.board[king_pos[0][0] + 1, king_pos[1][0]] = self.board[king_pos[0][0], king_pos[1][0]]
            self.board[king_pos[0][0], king_pos[1][0]] = 'E'
        if action == 4 and king_pos[0][0] - 1 >= 0 and king_pos[1][0] - 1 >= 0:  # up left
            self.board[king_pos[0][0] - 1, king_pos[1][0] - 1] = self.board[king_pos[0][0], king_pos[1][0]]
            self.board[king_pos[0][0], king_pos[1][0]] = 'E'
        if action == 5 and king_pos[0][0] - 1 >= 0 and king_pos[1][0] + 1 < self.height:  # up right
            self.board[king_pos[0][0] - 1, king_pos[1][0] + 1] = self.board[king_pos[0][0], king_pos[1][0]]
            self.board[king_pos[0][0], king_pos[1][0]] = 'E'
        if action == 6 and king_pos[0][0] + 1 < self.width and king_pos[1][0] - 1 >= 0:  # bottom left
            self.board[king_pos[0][0] + 1, king_pos[1][0] - 1] = self.board[king_pos[0][0], king_pos[1][0]]
            self.board[king_pos[0][0], king_pos[1][0]] = 'E'
        if action == 7 and king_pos[0][0] + 1 < self.width and king_pos[1][0] + 1 < self.height:  # bottom right
            self.board[king_pos[0][0] + 1, king_pos[1][0] + 1] = self.board[king_pos[0][0], king_pos[1][0]]
            self.board[king_pos[0][0], king_pos[1][0]] = 'E'
        

        # reward is negative for each step
        reward = -0.05

        # opponent covering area:
        bishop_pos = np.where(self.board == 'b')
        self.bishop = bishop_pos
        if bishop_pos[0]:
            temp = bishop_pos[0][0] - bishop_pos[1][0]
            if(king_pos[0][0] - king_pos[1][0] == temp or king_pos[0][0] + king_pos[1][0] == temp):
                reward = -10

        # any time the king reaches the first row, the game is done
        done = king_pos[0][0] == 1

        if done:
            reward = 10

        return self.board, reward, done, {}

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        # here is the board rendering:
        self.screen.fill("white")
        for row in range(self.height):
            for col in range(self.width):
                color = "white"
                if (row + col) % 2 == 0:
                    color = (117,150,86)

                else:
                    color = (238,238,210)

                pygame.draw.rect(self.screen, color, (col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size))
                if(row == 0):
                    # the first line is our goal and it should have a small shadow on the bottom:
                    pygame.draw.rect(self.screen, "black", (col * self.cell_size, row * self.cell_size + self.cell_size - 5, self.cell_size, 5))
        # here is the king initial place:
        king = pygame.image.load("chess-images/white-king.svg")
        king = pygame.transform.scale(king, (self.cell_size, self.cell_size))

        self.screen.blit(king, (self.king[1][0]* self.cell_size, self.king[0][0]* self.cell_size))

        # here is the opponent beshop:
        bishop = pygame.image.load("chess-images/black-bishop.svg")
        bishop = pygame.transform.scale(bishop, (self.cell_size, self.cell_size))

        if(self.bishop[0]):
            self.screen.blit(bishop, (self.bishop[1][0] * self.cell_size, self.bishop[0][0] * self.cell_size))
        
        print("rendering the board:")
        print(self.board)

        # flip() the display to put your work on screen
        pygame.display.flip()
        self.clock.tick(1)  # limits FPS to 1


if __name__ == "__main__":
    env = RacingKingsEnv()
    env.reset()
    for _ in range(500):
        action = env.action_space.sample()  # action = 0 or 1 or 2 ... to 7
        print('action', action)
        state, reward, done, info = env.step(action)
        env.render()
        if done:
            break