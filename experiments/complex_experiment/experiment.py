from collections import defaultdict

from shasta.base_experiment import BaseExperiment

from .custom_primitive import FormationWithPlanning
from .states import StatesExtractor


def group_actors_by_type(actor_groups):
    actor_type = defaultdict(list)
    for key, value in sorted(actor_groups.items()):
        actor_type[value[0].type].extend(value)
    return actor_type


class SearchingExperiment(BaseExperiment):
    def __init__(self, config, core, experiment_config=None, *args, **kargs):
        super().__init__(config, core, experiment_config, *args, **kargs)

        self.state_extractor = StatesExtractor(experiment_config, core)

        # Primitive setup
        self.actions = {}
        env_map = core.get_map()
        for i in range(6):
            self.actions[i] = FormationWithPlanning(env_map)

    def reset(self):
        """Called at the beginning and each time the simulation is reset"""
        pass

    def get_action_space(self):
        """Returns the action space"""
        pass

    def get_observation_space(self):
        """Returns the observation space"""
        pass

    def get_actions(self):
        """Returns the actions"""
        pass

    def apply_actions(self, actions, core):
        """Given the action, returns a carla.VehicleControl() which will be applied to the hero

        :param action: value outputted by the policy
        """
        # Get the actor group
        actor_groups = core.get_actor_groups()
        self.dones = []
        for i in range(6):
            done = self.actions[i].execute(actor_groups[i], target_pos=0)
            self.dones.append(done)

    def get_observation(self, observation, core):
        """Function to do all the post processing of observations (sensor data).

        :param sensor_data: dictionary {sensor_name: sensor_data}

        Should return a tuple or list with two items, the processed observations,
        as well as a variable with additional information about such observation.
        The information variable can be empty
        """
        actor_groups = core.get_actor_groups()
        grouped_by_type = group_actors_by_type(actor_groups)
        states = self.state_extractor.get_state(
            grouped_by_type['uav'], grouped_by_type['ugv']
        )
        return states, {}

    def get_done_status(self, observation, core):
        """Returns whether or not the experiment has to end"""
        actor_groups = core.get_actor_groups()
        grouped_by_type = group_actors_by_type(actor_groups)
        done = self.state_extractor.update_progrees(
            grouped_by_type['uav'], grouped_by_type['ugv']
        )
        return done

    def compute_reward(self, observation, core):
        """Computes the reward"""
        return 0