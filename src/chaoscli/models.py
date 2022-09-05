import shlex
import typing

import yaml


def _render_opt(key: str, value: typing.Any) -> typing.List[str]:

    if isinstance(value, bool):
        return [f"--{key}"] if value else []
    else:
        return [f"--{key}", shlex.quote(value)]
    pass


class CtkCommand:
    def __init__(self, **kwargs):
        self._conf = {**kwargs}

    @classmethod
    def from_str(cls, confstr: str):
        data = yaml.safe_load(confstr)
        return cls(**data)

    @classmethod
    def from_file(cls, filename: str):
        with open(filename, "r", encoding="UTF-8") as file:
            return cls.from_str(file.read())

    @property
    def conf(self):
        return self._conf

    def render(self, op_name: str = "run") -> typing.List[str]:
        cmd = ["chaos"]

        ctk_options = self.conf.get("chaos") or {}
        for k, v in ctk_options.items():
            cmd.extend(_render_opt(k, v))

        cmd.append(op_name)

        ctk_op_options = self.conf.get("run") or {}
        for k, v in ctk_op_options.items():
            cmd.extend(_render_opt(k, v))

        cmd.append(self.conf.get("experiment_path") or "experiment.yaml")

        return cmd
