import pygame
import gymnasium as gym
import math

homeImage = pygame.image.load('./delivery-images/home1.png')
restaurantImage = pygame.image.load('./delivery-images/restaurant.png')
treeImage0 = pygame.image.load('./delivery-images/tree.png')
treeImage1 = pygame.image.load('./delivery-images/tree1.png')
treeImage2 = pygame.image.load('./delivery-images/tree2.png')
treeImage3 = pygame.image.load('./delivery-images/tree3.png')
deliveryImage = pygame.image.load('./delivery-images/delivery.png')
deliveryWithBurgurImage = pygame.image.load('./delivery-images/delivery-with-burger.png')
holeImage = pygame.image.load('./delivery-images/hole.png')

navigations = [ (0, 1), (0, -1), (1, 0), (-1, 0) ]

# wirte a random stuff

class DeliveryEnv(gym.Env):
    """ initialises the delivery environment

    Args:
        no args
    """
    def __init__(self):
        """ 
            initialises the delivery environment
        """
        super().__init__()

        self.width = 10
        self.height = 10
        self.cell_size = 100
        self.action_space = gym.spaces.Discrete(4)
        self.customerPosition = (9, 9)
        self.restourantPosition = (0, 9)
        self.reset()

        # pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode((self.width * self.cell_size, self.height * self.cell_size))
        self.clock = pygame.time.Clock()


       
    def reset(self):
        """
         reset the environment and return the initial state and distance to goal
        """

        self.deliveryPosition = (0, 0)
        self.turn = 0
        self.gotFoodFromRestaurant = False

        
        self.treesArray = [
            (1, 1), (1, 6), (1, 7), (2, 4), (2, 5),
            (3, 1), (2, 2), (3, 3), (9, 4), (9, 5),
            (5,9), (6, 9)
        ]

        self.holesArray = [
            (4, 4), (4, 5), (8, 4), (8, 5)
        ]

        distance_to_goal = self.width + self.height
        return self.deliveryPosition, distance_to_goal


    def step(self, action):
        """
        take a step in the environment using an action including moving the delivery agent, checking if the delivery agent is at the restaurant position, customer position, or out of bounds
        args:
            action: int
        returns:
            deliveryPosition: tuple
            reward: float
            done: bool
            info: dict
        """
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
            reward += 0.5

        # going to customer without food is our hell state
        if self.deliveryPosition == self.customerPosition and not self.gotFoodFromRestaurant:
            print('Hell state!')
            reward += -10
            done = True

        # going to holes is also a hell state
        if self.deliveryPosition in self.holesArray:
            print('Hell state!')
            reward += -10
            done = True

        

        # check if the delivery agent is at the customer position
        if self.deliveryPosition == self.customerPosition and self.gotFoodFromRestaurant:
            print('Delivery made!')
            reward += 1
            done = True
        

        info = {
            'distance_to_goal': abs(self.deliveryPosition[0] - self.customerPosition[0]) + abs(self.deliveryPosition[1] - self.customerPosition[1]) 
            if self.gotFoodFromRestaurant 
            else abs(self.deliveryPosition[0] - self.restourantPosition[0]) + abs(self.deliveryPosition[1] - self.restourantPosition[1]) + self.width
        }
        return self.deliveryPosition, reward, done, info


    
        
    def _renderPicture(self, image, i, j):
        """
        a helper function to render a picture in the environment using a given png/svg file in the specified position
        args:
            image: pygame.image
            i: int
            j: int
        """
        pygame.draw.rect(self.screen, (255, 255, 255), (i * self.cell_size, j * self.cell_size, self.cell_size - 1, self.cell_size - 1))    
        scaledImage = pygame.transform.scale(image, (self.cell_size, self.cell_size))
        self.screen.blit(scaledImage, (i * self.cell_size, j * self.cell_size))
        pass
    
    def _renderTree(self, i, j, turn=0):
        """
        a helper function to render a tree in the environment
        args:
            i: int
            j: int
            turn: int
        """
        # sorry, I am not good at drawing trees -\_(-_-)_/-
        # but it should feel like it is windy
        treeImages = [treeImage0, treeImage1, treeImage2, treeImage3, treeImage2, treeImage1]
        # it will render a new tree every 30 turns
        randomTree = treeImages[math.floor(turn / 30) % 4]
        gap = self.cell_size / 3
        pygame.draw.rect(self.screen, (255, 255, 255), (i * self.cell_size, j * self.cell_size, self.cell_size - 1, self.cell_size - 1))    
        scaledImage = pygame.transform.scale(randomTree, (self.cell_size - gap, self.cell_size))
        self.screen.blit(scaledImage, (i * self.cell_size + gap / 2, j * self.cell_size))
        pass
    
    def close(self):
        """
        close the environment
        """
        pygame.quit()
        pass
    

    def render(self):
        """
        render the environment, draw the environment, trees, delivery agent, restaurant, customer, and update the screen
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close()
        self.screen.fill((200, 200, 200))

        # draw the environment
        for i in range(self.width):
            for j in range(self.height):
                color = (255, 255, 255)
                if (i, j) == self.deliveryPosition:
                    if(self.gotFoodFromRestaurant):
                        self._renderPicture(deliveryWithBurgurImage, i, j)
                    else:
                        self._renderPicture(deliveryImage, i, j)
                    continue
                if (i, j) == self.customerPosition:
                    self._renderPicture(homeImage, i, j)
                    continue
                if (i, j) == self.restourantPosition:
                    self._renderPicture(restaurantImage, i, j)
                    continue
                if (i, j) in self.treesArray:
                    self._renderTree(i, j, self.turn)
                    continue
                if (i, j) in self.holesArray:
                    self._renderPicture(holeImage, i, j)
                    continue
                pygame.draw.rect(self.screen, color, (i * self.cell_size, j * self.cell_size, self.cell_size - 1, self.cell_size - 1))    
        

        # update the screen
        pygame.display.flip()
        self.clock.tick(6)

        #show the turn number on the window title and console
        print(f'Turn: {self.turn}')
        pygame.display.set_caption(f'Turn: {self.turn}')

        pass

"""
end of the DeliveryEnvClass implementation
start of the usage sample of the DeliveryEnv
"""

def dfs(env, start, goal, path= [], shortest= None, visited = None) -> list:
    """
    a dfs function to find the shortest path from start to goal in the environment
    (this part developed in the practical season as Adi suggested, probably not part of the criteria of the assignment, but I thought it would be nice to include it as well)
    args:
        env: DeliveryEnv
        start: tuple
        goal: tuple
        path: list
        shortest: list
        visited: set
    returns:
        shortest: list
    """
    x, y = start
    if(start == goal):
        return path
    if visited is None:
        visited = set()

    if(shortest != None and len(path) >= len(shortest)):
        return None
    
    visited.add(start)
    for moveIndex in range(len(navigations)):
        dx, dy = navigations[moveIndex]
        nx, ny = x + dx, y + dy
        if nx >= 0 and nx < env.width and ny >= 0 and ny < env.height and (nx, ny) not in env.treesArray and (nx, ny) not in visited:
            if (nx, ny) not in path:
                new_path = dfs(env, (nx, ny), goal, path + [moveIndex], shortest, visited)
                if new_path != None:
                    shortest = new_path
    visited.remove(start)
    return shortest

def _renderAlert(env, message):
    """
    a helper function to render an alert message on the screen, and wait for 3 seconds to close it
    """
    pygame.display.set_caption(message)
    env.render()
    pygame.time.wait(3000)

if __name__ == '__main__':
    env = DeliveryEnv()
    env.reset()

    # use dfs to find the shortest path to restaurant (complete search!)
    actions = dfs(env, env.deliveryPosition, env.restourantPosition) + dfs(env, env.restourantPosition, env.customerPosition)

    reward = 0
    for action in actions:
        pos, reward, done, info = env.step(action)
        env.render()
        if done:
            break
    _renderAlert(env, 'Delivery completed! Reward:' + str(reward))
    env.close()

        