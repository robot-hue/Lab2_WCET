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

def nondeterminism_ratio(fragment: list[Operation], model: ProcessorModel) -> float:
    """Вычисление коэффициента недетерминизма как отношения WCET к BCET."""
    best_time = bcet(fragment, model)
    if best_time == 0:
        return 0.0
    return wcet(fragment, model) / best_time

def source_breakdown(fragment: list[Operation], model: ProcessorModel) -> dict[str, int]:
    """Раздельный расчет накладных расходов на кэш-промахи и ошибки предсказателя."""
    total_mem_accesses = sum(op.memory_accesses for op in fragment)
    total_branches = sum(op.branches for op in fragment)
    return {
        "base_cost_total": len(fragment) * model.base_cost,
        "memory_penalty_total": total_mem_accesses * model.cache_miss_penalty,
        "branch_penalty_total": total_branches * model.branch_mispredict_penalty,
        "total_memory_accesses": total_mem_accesses,
        "total_branches": total_branches,
    }
