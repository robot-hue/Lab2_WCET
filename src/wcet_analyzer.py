from dataclasses import dataclass
import json
import os
import sys

@dataclass(frozen=True)
class ProcessorModel:
    base_cost: int
    cache_miss_penalty: int
    branch_mispredict_penalty: int
    deadline: int

@dataclass(frozen=True)
class Operation:
    name: str
    op_type: str
    memory_accesses: int
    branches: int

def load_configuration(file_path: str) -> tuple[ProcessorModel, list[Operation]]:
    """Чтение файла конфигурации без магических чисел."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл конфигурации не найден: {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    proc_data = data["processor"]
    model = ProcessorModel(
        base_cost=proc_data["base_cost"],
        cache_miss_penalty=proc_data["cache_miss_penalty"],
        branch_mispredict_penalty=proc_data["branch_mispredict_penalty"],
        deadline=proc_data["deadline"],
    )
    
    operations = [
        Operation(
            name=op["name"],
            op_type=op["op_type"],
            memory_accesses=op["memory_accesses"],
            branches=op["branches"],
        )
        for op in data["operations"]
    ]
    return model, operations
