import unittest
from chaoscli import models


class TestModels(unittest.TestCase):
    def test_command_run(self):
        template = """
        job_id: 1234
        chaos:
          verbose: true
        run:
          config-file: config.yaml
        experiment_path: myexperiment.yaml"""

        cmd = models.CtkCommand().from_str(template).render()

        self.assertListEqual(
            cmd,
            [
                "chaos",
                "--verbose",
                "run",
                "--config-file",
                "config.yaml",
                "myexperiment.yaml",
            ],
        )
