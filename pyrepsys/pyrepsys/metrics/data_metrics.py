import csv
import os.path

from .metrics_base import Metric
from pyrepsys.helper_types import SimulationEvent

class ScenarioData:
    def __init__(self, scenario_name):
        self.name = scenario_name
        self.rounds = []
        self.agent_reputations = {}

class ReputationsByRoundsData(Metric):
    def __init__(self):
        super().__init__()
        self.add_event_of_interest(SimulationEvent.END_OF_ROUND)
        self.name = "Agent Reputations By Rounds"
        self.scenarios_data = []
    
    def prepare_new_scenario(self, scenario):
        self.scenarios_data.append( ScenarioData(scenario) )

    def calculate(self, **data):
        agents_data = data["agents_data"]
        round_number = data["round_number"]

        data = self.scenarios_data[-1]
        
        data.rounds.append(round_number)
        for agent in agents_data:
            try:
                agent_reps_list = data.agent_reputations[agent.ID]
            except KeyError:
                agent_reps_list = []
                data.agent_reputations[agent.ID] = agent_reps_list
            agent_reps_list.append(agent.global_reputation)

    def export(self, target_dir):
        for scenario in self.scenarios_data:
            csv_file_name = scenario.name + '.csv'
            csv_file_path = os.path.join(target_dir, csv_file_name)

            with open(csv_file_path, mode='w') as file:
                writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                writer.writerow(['Agent#'] + scenario.rounds)
                for agent_ID, reputations in scenario.agent_reputations.items():
                    writer.writerow([agent_ID] + reputations )

