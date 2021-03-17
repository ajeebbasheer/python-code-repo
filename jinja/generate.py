import os
from jinja2 import FileSystemLoader, Environment
JINJA_TEMPLATE = "template.j2"
PROJECT_DIR = "/home/ajeeb/workspace/python-code-repo/jinja"

obj = {
    "instance_name": "Test-Instance",
    "network_uuid": "f30cc45d-e80c-4efb-811e-f10bb526f616",
    "security_group": "default",
    "key_name": "ajeebmb",
    "flavor_name": "Test-Flavor"
}

def generate_configurations():
    jinja_env = Environment(
        loader=FileSystemLoader(PROJECT_DIR),
        trim_blocks=True,
        lstrip_blocks=True
    )
    input_json = jinja_env.get_template(JINJA_TEMPLATE).render(obj)
    print(f"{input_json}")
    
if __name__ == "__main__":
    generate_configurations()