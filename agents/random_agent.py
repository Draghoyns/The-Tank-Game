from base_agent import BaseAgent

class RandomAgent(BaseAgent):
    def select_action(self, state):
        return self.action_space.sample()  # Chooses random action
    
    def learn(self, *args, **kwargs):
        pass