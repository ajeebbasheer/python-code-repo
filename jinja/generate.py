import os
import json
from jinja2 import FileSystemLoader, Environment
JINJA_TEMPLATE = "template.j2"
PROJECT_DIR = "/home/ajeeb/workspace/python-code-repo/jinja"

values = {
    "instance_name": "Test-Instance",
    "image_id": "d-e80c-4efb-811e-f10bb526f61",
    "network_id": "f30cc45d-e80c-4efb-811e-f10bb526f616",
    "security_group": "default",
    "key_name": "ajeebmb",
    "flavor_name": "Test-Flavor",
    "host_aggregate_name": "host_aggregate_name"
}

class Templates:
    ROBOT_LIBRARY_SCOPE = 'API TEST'
    def __init__(self):
        pass
    def generate_configurations(self):
        jinja_env = Environment(
            loader=FileSystemLoader(PROJECT_DIR),
            trim_blocks=True,
            lstrip_blocks=True
        )
        input_json = jinja_env.get_template(JINJA_TEMPLATE).render(values)
        return json.loads(input_json)
       
if __name__ == "__main__":
    obj = Templates()
    print(f"{obj.generate_configurations()}")