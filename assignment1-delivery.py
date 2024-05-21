import pygame
import gymnasium as gym
import numpy as np
import math

homeImage = pygame.image.load('./delivery-images/home1.png')
restaurantImage = pygame.image.load('./delivery-images/restaurant.png')
treeImage0 = pygame.image.load('./delivery-images/tree.png')
treeImage1 = pygame.image.load('./delivery-images/tree1.png')
treeImage2 = pygame.image.load('./delivery-images/tree2.png')
treeImage3 = pygame.image.load('./delivery-images/tree3.png')
deliveryImage = pygame.image.load('./delivery-images/delivery.png')

navigations = [ (0, 1), (0, -1), (1, 0), (-1, 0) ]

class DeliveryEnv(gym.Env):
    def __init__(self):
        super().__init__()

        self.width = 10
        self.height = 10
        self.cell_size = 100
        self.action_space = gym.spaces.Discrete(4)
        self.observation_space = gym.spaces.Box(low=-1, high=1, shape=(self.width, self.height, 1))
        
        self.reset()

        # pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode((self.width * self.cell_size, self.height * self.cell_size))
        self.clock = pygame.time.Clock()

    def reset(self):

        self.deliveryPosition = (0, 0)
        self.customerPosition = (9, 9)
        self.restourantPosition = (0, 9)

        self.turn = 0
        self.gotFoodFromRestaurant = False

        
        self.treesArray = [
            (1, 1), (1, 6), (1, 7), (2, 4), (2, 5),
            (3, 1), (2, 2), (3, 3), (9, 4), (9, 5),
            (5,9), (6, 9)
        ]

        distance_to_goal = self.width + self.height
        return self.deliveryPosition, distance_to_goal

    def step(self, action):
        # reward is negative for each step
        reward = -0.05
        done = False
        self.turn += 1
        # move the delivery agent
        move = navigations[action]
        tempDeliveryPosition = (self.deliveryPosition[0] + move[0], self.deliveryPosition[1] + move[1])

        # dont move if there is a tree, or out of bounds
        if tempDeliveryPosition in self.treesArray or tempDeliveryPosition[0] < 0 or tempDeliveryPosition[0] >= self.width or tempDeliveryPosition[1] < 0 or tempDeliveryPosition[1] >= self.height:
            return self.deliveryPosition, reward, done, {}
        
        self.deliveryPosition = tempDeliveryPosition

        # check if the delivery agent is at the restaurant position
        if self.deliveryPosition == self.restourantPosition:
            self.gotFoodFromRestaurant = True
            print('Got food from restaurant!')
            reward = 0.5

        # going to customer without food is our hell state
        if self.deliveryPosition == self.customerPosition and not self.gotFoodFromRestaurant:
            print('Hell state!')
            reward = -1
            done = True

        # check if the delivery agent is at the customer position
        if self.deliveryPosition == self.customerPosition and self.gotFoodFromRestaurant:
            print('Delivery made!')
            reward = 1
            done = True
        

        info = {
            'distance_to_goal': abs(self.deliveryPosition[0] - self.customerPosition[0]) + abs(self.deliveryPosition[1] - self.customerPosition[1]) 
            if self.gotFoodFromRestaurant 
            else abs(self.deliveryPosition[0] - self.restourantPosition[0]) + abs(self.deliveryPosition[1] - self.restourantPosition[1]) + self.width
        }
        return self.deliveryPosition, reward, done, info


    def renderPicture(self, image, i, j):
        pygame.draw.rect(self.screen, (255, 255, 255), (i * self.cell_size, j * self.cell_size, self.cell_size - 1, self.cell_size - 1))    
        scaledImage = pygame.transform.scale(image, (self.cell_size, self.cell_size))
        self.screen.blit(scaledImage, (i * self.cell_size, j * self.cell_size))

    def renderTree(self, i, j, turn=0):
        # sorry, I am not good at drawing trees -\_(-_-)_/-
        # but it should feel like it is windy
        treeImages = [treeImage0, treeImage1, treeImage2, treeImage3, treeImage2, treeImage1]
        # it will render a new tree every 30 turns
        randomTree = treeImages[math.floor(turn / 30) % 4]
        gap = self.cell_size / 3
        pygame.draw.rect(self.screen, (255, 255, 255), (i * self.cell_size, j * self.cell_size, self.cell_size - 1, self.cell_size - 1))    
        scaledImage = pygame.transform.scale(randomTree, (self.cell_size - gap, self.cell_size))
        self.screen.blit(scaledImage, (i * self.cell_size + gap / 2, j * self.cell_size))

    def close(self):
        pygame.quit()

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()

        self.screen.fill((200, 200, 200))
        print('rendering...')

        # draw the environment
        for i in range(self.width):
            for j in range(self.height):
                color = (255, 255, 255)
                if (i, j) == self.deliveryPosition:
                    self.renderPicture(deliveryImage, i, j)
                    continue
                if (i, j) == self.customerPosition:
                    self.renderPicture(homeImage, i, j)
                    continue
                if (i, j) == self.restourantPosition:
                    self.renderPicture(restaurantImage, i, j)
                    continue
                if (i, j) in self.treesArray:
                    self.renderTree(i, j, self.turn)
                    continue

                pygame.draw.rect(self.screen, color, (i * self.cell_size, j * self.cell_size, self.cell_size - 1, self.cell_size - 1))    
        

        # update the screen
        pygame.display.flip()
        self.clock.tick(60)

        #show the turn
        print(f'Turn: {self.turn}')
        pygame.display.set_caption(f'Turn: {self.turn}')


if __name__ == '__main__':
    env = DeliveryEnv()
    env.reset()
    for _ in range(100000):
        pos, reward, done, info = env.step(env.action_space.sample())
        print('Info:', info)
        env.render()
        if done:
            env.close()
    env.close()

        