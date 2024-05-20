from VRPTW.structure import Problem, Route
import itertools


class DummyHeuristic:
    def __init__(self, problem: Problem):
        self.problem: Problem = problem

    def get_solution(self):
        def get_available_customers():
            return sorted(filter(lambda x: not x.is_serviced, self.problem.customers), key=lambda x: x.due_date)

        solution = [[] for _ in range(self.problem.vehicle_number)]  # Initialize routes for each vehicle
        while len(get_available_customers()) > 0:
            customers = get_available_customers()
            for i in range(self.problem.vehicle_number):
                route = solution[i]
                for customer in customers:
                    if Route(self.problem, route + [customer]).is_feasible:
                        customer.is_serviced = True
                        route.append(customer)
                        break  # Assign the customer to the first feasible vehicle
        return solution


class LocalSearch:
    def __init__(self, problem: Problem):
        self.problem: Problem = problem

    def optimize(self, solution: list) -> list:
        new_solution = [list(route) for route in solution]  # Create a deep copy of the solution
        for i in range(len(new_solution)):
            is_stucked = False
            while not is_stucked:
                route = new_solution[i]
                is_stucked = True
                for k, j in itertools.combinations(range(len(route)), 2):
                    new_route = Route(self.problem, two_opt(route, k, j))
                    if new_route.is_feasible:
                        if new_route.total_distance < Route(self.problem, route).total_distance:
                            new_solution[i] = new_route.customers
                            is_stucked = False
        return new_solution


class IteratedLocalSearch(LocalSearch):
    def __init__(self, problem: Problem, obj_func=None):
        super().__init__(problem)
        if not obj_func:
            obj_func = self.problem.obj_func
        self.obj_func = obj_func
        self.initial_solution = DummyHeuristic(problem).get_solution()

    def perturbation(self, routes: list) -> list:
        best = [Route(self.problem, route) for route in routes]
        is_stucked = False
        while not is_stucked:
            is_stucked = True
            for i, j in itertools.combinations(range(len(best)), 2):
                for k, l in itertools.product(range(len(best[i]) + 2), range(len(best[j]) + 2)):
                    for func in [cross, insertion, swap]:
                        c1, c2 = func(best[i], best[j], k, l)
                        r1, r2 = Route(self.problem, c1), Route(self.problem, c2)
                        if r1.is_feasible and r2.is_feasible:
                            if r1.total_distance + r2.total_distance < best[i].total_distance + best[j].total_distance:
                                best[i] = r1.customers
                                best[j] = r2.customers
                                is_stucked = False
            best = list(filter(lambda x: len(x) != 0, best))
        return best

    def execute(self):
        best = self.optimize(self.initial_solution)
        print("Local search solution:")
        for idx, route in enumerate(best):
            print(f"Route {idx + 1}: {route}")
            print("Total distance:", Route(self.problem, route).total_distance)
        print("Total distance for all vehicles:", self.obj_func(best))

        is_stucked = False
        while not is_stucked:
            is_stucked = True
            new_solution = self.perturbation(best)
            new_solution = self.optimize(new_solution)
            if self.obj_func(new_solution) < self.obj_func(best):
                is_stucked = False
                best = list(filter(lambda x: len(x) != 0, new_solution))
                print("ILS step:")
                for idx, route in enumerate(best):
                    print(f"Route {idx + 1}: {route}")
                    print("Total distance:", Route(self.problem, route).total_distance)
                print("Total distance for all vehicles:", self.obj_func(best))
        return best


def two_opt(a, i, j):
    if i == 0:
        return a[j:i:-1] + [a[i]] + a[j + 1:]
    return a[:i] + a[j:i - 1:-1] + a[j + 1:]


def cross(a, b, i, j):
    return a[:i] + b[j:], b[:j] + a[i:]


def insertion(a, b, i, j):
    if len(a) == 0:
        return a, b
    while i >= len(a):
        i -= len(a)
    return a[:i] + a[i + 1:], b[:j] + [a[i]] + b[j:]


def swap(a, b, i, j):
    if i >= len(a) or j >= len(b):
        return a, b
    a, b = a.copy(), b.copy()
    a[i], b[j] = b[j], a[i]
    return a, b


if __name__ == "__main__":
    # Define your problem instance and call the execute method of IteratedLocalSearch
    # For example:
    problem = Problem(...)
    ils = IteratedLocalSearch(problem)
    ils.execute()