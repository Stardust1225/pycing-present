from GenOnBack.SolverModel import SolverModel

content = []
content.append('tool_mapping_getitemstring:names')
content.append('tool_mapping_getitemstring:formats')

solver = SolverModel(content)
print(solver.produce_object())