import os
import sys
import inspect
import importlib.util

from pathlib import Path
from typing import Type, List, TypeVar
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

T = TypeVar('T')

def get_automation_instances_of_type(hass: HomeAssistant, config_entry:ConfigEntry, entity_type: Type[T]) -> List[T]:
    instances = []
    current_dir = Path(__file__).parent
    root_path = (current_dir / "automations").resolve()

    if not root_path.exists():
        raise FileNotFoundError(f"The directory doesn't exist {root_path}")

    for file_path in root_path.rglob("*.py"):
        if file_path.name.startswith('__'):
            continue

        try:
            relative_path = file_path.relative_to(current_dir)
            module_name = str(relative_path).replace(os.sep, '.').rstrip('.py')
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            for name, obj in inspect.getmembers(module):
                if name.startswith('__'):
                    continue

                if (inspect.isclass(obj) and issubclass(obj, entity_type) and obj != entity_type):
                    class_module = inspect.getmodule(obj)
                    if class_module and str(class_module.__file__).startswith(str(root_path)):
                        instance = obj(hass, config_entry)
                        instances.append(instance)
        except Exception as e:
            print(f"Error importing {file_path}: {e}")
            
    return instances

def get_domain(dir: str) -> str:
    return Path(dir).parent.name

def get_main_domain() -> str:
    return get_domain(__file__)