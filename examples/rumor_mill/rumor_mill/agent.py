from mesa.discrete_space import CellAgent


class Person(CellAgent):
    """
    A person agent that can know and spread a rumor.
    """

    def __init__(self, model, cell, rumor_spread_chance=0.5, recovery_rate=0.0, color=None):
        """
        Initialize a Person agent.

        Args:
            model: The model instance
            cell: The cell where this agent is located
            rumor_spread_chance: Probability of successfully spreading rumor (0.0-1.0)
            color: Agent's color (red if knows rumor initially, blue otherwise)
        """
        super().__init__(model)
        self.cell = cell
        self.knows_rumor = False  # Whether agent knows the rumor
        self.times_heard = 0  # Total cumulative times agent has heard the rumor
        self.times_heard_this_step = 0  # Times heard in current step
        self.newly_learned = False  # Whether agent just learned the rumor this step
        self.rumor_spread_chance = rumor_spread_chance
        self.recovery_rate = recovery_rate
        self.just_recovered = False
        self.color = color if color is not None else self.random.choice(["red", "blue"])

    def step(self):
        """
        Agent behavior each step: if knows rumor, tell a random neighbor.
        """
        if not self.knows_rumor:
             return
        # Chance to forget the rumor and become uninformed again
        if self.random.random() < self.recovery_rate:
            self.knows_rumor = False
            self.just_recovered = True
            return

        neighbors = [
           agent for agent in self.cell.neighborhood.agents if agent != self
        ]
        if neighbors:
           neighbor = self.random.choice(neighbors)
           if (
               not neighbor.knows_rumor
               and self.random.random() < self.rumor_spread_chance
           ):
                neighbor.knows_rumor = True
                neighbor.newly_learned = True
        neighbor.times_heard += 1
        neighbor.times_heard_this_step += 1
