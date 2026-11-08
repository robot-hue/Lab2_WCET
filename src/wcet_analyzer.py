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

def best_case(op: Operation, model: ProcessorModel) -> int:
    """Расчет идеального времени выполнения инструкции (без промахов и ошибок)."""
    return model.base_cost

def worst_case(op: Operation, model: ProcessorModel) -> int:
    """Расчет максимального времени с учетом штрафов за промахи кэша и ветвления."""
    return (
        model.base_cost
        + op.memory_accesses * model.cache_miss_penalty
        + op.branches * model.branch_mispredict_penalty
    )

def bcet(fragment: list[Operation], model: ProcessorModel) -> int:
    """Вычисление суммарного наилучшего времени выполнения всего блока (BCET)."""
    return sum(best_case(op, model) for op in fragment)

def wcet(fragment: list[Operation], model: ProcessorModel) -> int:
    """Вычисление суммарного наихудшего времени выполнения всего блока (WCET)."""
    return sum(worst_case(op, model) for op in fragment)
