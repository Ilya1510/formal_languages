# graph - dict (v -> [(w_i, c_i)])
# Вершина с номером 0 всегда начальная


# Находит вершины достижимые из данного множества вершин, по ребру с заданным символом
def find_step_vertices(graph, cur_vs, c):
    st_vertices = set()
    for v in cur_vs:
        for next_v, symbol in graph[v]:
            if symbol == c:
                st_vertices.add(next_v)
    return tuple(st_vertices)


# Выдаёт номер минимальной вершины, которой ещё нет в графе,
# её можно использовать как фиктивную, чтобы сделать автомат полным
def get_new_vertex(graph):
    n = len(graph)
    used = [False] * (n + 1)
    for v in graph:
        if v < n:
            used[v] = True
    fict_v = -1
    for ind, u in enumerate(used):
        if not u:
            fict_v = ind
            break
    return fict_v


# Делает автомат полным, добавляя фиктивную вершину
def make_full(graph, symbols):
    fict_v = get_new_vertex(graph)
    graph[fict_v] = []
    for v in graph:
        for c in symbols:
            if c not in [x[1] for x in graph[v]]:
                graph[v].append((fict_v, c))
    return graph


# Приводит пНКА к пДка
def to_dka(graph, finishes, symbols):
    # Два словаря: состояние в новом автомате <-> подмно-во вершин начально
    num_to_set = dict()
    set_to_num = dict()
    num_to_set[0] = tuple([0])
    set_to_num[tuple([0])] = 0

    new_graph = dict()
    # Очередь (по факту стек) ещё не просмотренных состояний
    queue_states = [0]
    while len(queue_states) != 0:
        # Вынимаем сотосяние
        ind_state = queue_states[-1]
        queue_states.pop()
        new_graph[ind_state] = []
        state_vertices = num_to_set[ind_state]
        for c in symbols:
            # Находим в какое множество вершин начального графа оно ведёт
            set_step_vertices = find_step_vertices(graph, state_vertices, c)
            # Если состояние новое, его надо положить в очередь
            if set_step_vertices not in set_to_num:
                new_state_number = len(num_to_set)
                set_to_num[set_step_vertices] = new_state_number
                num_to_set[new_state_number] = set_step_vertices
                queue_states.append(new_state_number)
            # Добавляем ребро в новом графе
            new_graph[ind_state].append((set_to_num[set_step_vertices], c))

    # Новое множество финальных вершин - все состояния, содержащие хотя бы одно финальное в начальном графе
    new_finish = []
    for num_state in num_to_set:
        is_contain_finish = False
        for f in finishes:
            if f in num_to_set[num_state]:
                is_contain_finish = True
        if is_contain_finish:
            new_finish.append(num_state)
    return [new_graph, new_finish, symbols, num_to_set]


def decrease_states(graph, finishes, symbols):
    n = len(graph)
    comp_count = 2
    v_comp = dict()
    # Начальные классы экв-сти - завершающие и не завершающие вершины
    for v in graph:
        v_comp[v] = 0
    for v_f in finishes:
        v_comp[v_f] = 1
    is_something_changed = True
    while is_something_changed:
        is_something_changed = False
        one_step = dict()
        all_states = dict()
        # Теперь компонента вершины определяется, компонентой в которой она была и
        # кортежем из кмпонент вершин, в которые из неё ведут рёбра
        for v in graph:
            one_step[v] = tuple([v_comp[find_step_vertices(graph, [v], c)[0]] for c in symbols])
            if (v_comp[v], one_step[v]) not in all_states:
                all_states[(v_comp[v], one_step[v])] = len(all_states)
        v_comp_new = dict()
        for v in graph:
            v_comp_new[v] = all_states[(v_comp[v], one_step[v])]
        comp_count_new = len(all_states)
        # Если кол-во компонент связности изменилось, а их могло только увеличится,
        # то надо запустить ещё одну итерацию "дробления"
        if comp_count_new != comp_count:
            is_something_changed = True
            v_comp = v_comp_new
            comp_count = comp_count_new

    # Теперь строим новый граф, вершинами которого яв-ся классы эквивалентности начально графа
    new_graph = dict()
    for v in range(comp_count):
        new_graph[v] = []
    for v1 in graph:
        for v2, c in graph[v1]:
            w1 = v_comp[v1]
            w2 = v_comp[v2]
            if (w2, c) not in new_graph[w1]:
                new_graph[w1].append((w2, c))
    new_finish = set()
    for v in finishes:
        v_st = v_comp[v]
        new_finish.add(v_st)
    return [new_graph, new_finish, symbols, v_comp]


# Граф из 3-го домашнего задания - неполный, недетерминированный, неминимальный.
G = {0: [(0, 'a'), (1, 'a'), (0, 'b'), (4, 'a')],
     1: [(2, 'a')],
     2: [(2, 'a'), (2, 'b'), (3, 'b')],
     3: [(6, 'b')],
     4: [(5, 'b')],
     5: [(6, 'a')],
     6: [(7, 'a'), (6, 'b')],
     7: [(7, 'b')]
     }

G_dka, f_dka, symbols_dka, num_to_set = to_dka(make_full(G, ['a', 'b']), [7], ['a', 'b'])
G_mdka, f_mdka, symbols_mdka, v_comp = decrease_states(G_dka, f_dka, ['a', 'b'])

for key, value in G_mdka.items():
    print(key, value)
print(f_mdka)

# Вот вывод программы:
'''
0 [(1, 'a'), (0, 'b')]
1 [(2, 'a'), (3, 'b')]
2 [(2, 'a'), (21, 'b')]
3 [(4, 'a'), (0, 'b')]
4 [(5, 'a'), (6, 'b')]
5 [(2, 'a'), (14, 'b')]
6 [(7, 'a'), (8, 'b')]
7 [(5, 'a'), (12, 'b')]
8 [(9, 'a'), (8, 'b')]
9 [(2, 'a'), (10, 'b')]
10 [(4, 'a'), (11, 'b')]
11 [(1, 'a'), (11, 'b')]
12 [(7, 'a'), (13, 'b')]
13 [(9, 'a'), (13, 'b')]
14 [(15, 'a'), (16, 'b')]
15 [(5, 'a'), (17, 'b')]
16 [(5, 'a'), (16, 'b')]
17 [(18, 'a'), (19, 'b')]
18 [(5, 'a'), (20, 'b')]
19 [(5, 'a'), (19, 'b')]
20 [(18, 'a'), (16, 'b')]
21 [(15, 'a'), (19, 'b')]
{5, 7, 9, 10, 11, 12, 13, 14, 16, 18, 20}
'''
