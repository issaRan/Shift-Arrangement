import heapq
from enum import Enum


class Indices(Enum):
    DAY = 0
    SHIFT = 1
    EMP_I = 2


# Constants
SHIFTS_PER_DAY = 3
DAYS_PER_WEEK = 5
EMPLOYEES_N = 4
SHIFTS_EMP_N = [2, 1, 1]

# A requests list example for debugging.
req_example = [[[4, 4, 4], [4, 4, 4], [4, 4, 4], [4, 4, 4], [4, 4, 4]],
               [[3, 3, 3], [3, 3, 3], [3, 3, 3], [3, 3, 3], [3, 3, 3]],
               [[2, 2, 2], [2, 2, 2], [2, 2, 2], [2, 2, 2], [2, 2, 2]],
               [[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 1, 1]]]


# The model for the shifts assignment.
class Model:

    # Constructor.
    def __init__(self, employees_n, requests, num_days, num_shifts, chooser, shifts_emp_n):
        self.employees_n = employees_n  # The number of employees.
        self.shifts_emp_n = shifts_emp_n
        self.num_days = num_days
        self.num_shifts = num_shifts
        self.chooser = chooser  # The method to choose an employee for a given shift.
        self.requests = requests  # A list of the shift requests.
        self.average = 0
        self.employees_percents = None  # A real time updating list of satisfaction percentages of the employees.
        self.employees_request_units = None  # The employees' unit values - used in percentage calculations.
        self.assignments = None  # A list for the assignments.

    def reset_model(self):
        self.average = 0
        self.employees_percents = [0 for i in range(
            self.employees_n)]
        self.employees_request_units = [None for i in range(
            self.employees_n)]
        self.fill_employees_requests_units()
        self.assignments = [[None for j in range(self.num_shifts)] for i in
                            range(self.num_days)]

    # Calculate the unit values for every employee - Used in percentage calculations.
    def fill_employees_requests_units(self):
        for emp_i in range(self.employees_n):
            try:
                self.employees_request_units[emp_i] = 1 / sum(
                    self.requests[emp_i][i][j] for j in range(SHIFTS_PER_DAY) for i in range(DAYS_PER_WEEK))
            except ZeroDivisionError:
                self.employees_request_units[emp_i] = 0

    # The function that generates the assignment.
    def make_assignments(self):
        self.reset_model()
        if self.employees_n < sum(self.shifts_emp_n):
            raise ValueError("Invalid ratio between the number of shifts per day and the number of employees.")
        for i in range(self.num_days):
            for j in range(self.num_shifts):
                # self.make_choice((i, j))
                self.make_choice({Indices.DAY: i, Indices.SHIFT: j})
                # print(str(self.employees_percents))
        assignments = self.assignments
        return assignments

    # Update the employees' satisfaction percentage and the model's satisfaction average.
    def update_avg(self, indices):
        emps_i = indices[Indices.EMP_I]
        units = [self.employees_request_units[emp_i] for emp_i in emps_i]

        diffs = [self.requests[i][indices[Indices.DAY]][indices[Indices.SHIFT]] * unit for i, unit in
                 zip(emps_i, units)]

        for i in range(len(emps_i)):
            self.employees_percents[emps_i[i]] += diffs[i]
            self.average += diffs[i] / self.employees_n

    # Make a single assignment.
    def make_choice(self, indices):
        choice = self.chooser(self, indices)
        # print(choice, end=", ")
        self.assignments[indices[Indices.DAY]][indices[Indices.SHIFT]] = choice
        indices[Indices.EMP_I] = choice
        self.update_avg(indices)

    # Boolean method to check if employee is already working on the given day.
    def already_assigned_in_day(self, indices):
        for shift in self.assignments[indices[Indices.DAY]]:
            if shift is not None and indices[Indices.EMP_I] in shift:
                return True
        return False

    @staticmethod
    # My implementation for argmax for max n elements.
    def arg_n_max(n, arr):
        max_vals = heapq.nlargest(n, arr)
        res = []
        for i in range(n):
            appearances = [j for j, n in enumerate(arr) if arr[j] == max_vals[i]]
            idx = max_vals[:i].count(max_vals[i])
            temp = appearances[idx]
            res.append(temp)
        return res

    @staticmethod
    # My implementation for argmin for min n elements.
    def arg_n_min(n, arr):
        min_vals = heapq.nsmallest(n, arr)
        res = []
        for i in range(n):
            appearances = [j for j, n in enumerate(arr) if arr[j] == min_vals[i]]
            idx = min_vals[:i].count(min_vals[i])
            temp = appearances[idx]
            res.append(temp)
        return res

    # Print the employees' satisfaction percentages.
    def print_percentages(self):
        for i in range(self.employees_n):
            print(f"Employee no.{i + 1}: {self.employees_percents[i] * 100}%")


# Choose the employee who ranked this shift the highest.
def chooser1(model, indices):
    lst = [model.requests[i][indices[Indices.DAY]][indices[Indices.SHIFT]] if
           not model.already_assigned_in_day({Indices.EMP_I: i, Indices.DAY: indices[Indices.DAY]}) else float('-inf')
           for i in range(model.employees_n)]
    return Model.arg_n_max(model.shifts_emp_n[indices[Indices.SHIFT]], lst)


# Choose the employee whose percentage is the lowest.
def chooser2(model, indices):
    lst = [model.employees_percents[i] if
           not model.already_assigned_in_day({Indices.EMP_I: i, Indices.DAY: indices[Indices.DAY]}) else float('inf')
           for i in
           range(model.employees_n)]
    return Model.arg_n_min(model.shifts_emp_n[indices[Indices.SHIFT]], lst)


# Choose the employee whose the lowest from the average.
def chooser3(model, indices):
    lst = [model.average - model.employees_percents[i] if
           not model.already_assigned_in_day({Indices.EMP_I: i, Indices.DAY: indices[Indices.DAY]}) else float('-inf')
           for i in
           range(model.employees_n)]
    return Model.arg_n_max(model.shifts_emp_n[indices[Indices.SHIFT]], lst)


def chooser4(model, indices):
    lst = [(model.employees_percents[i] + model.requests[i][indices[Indices.DAY]][indices[Indices.SHIFT]] *
            model.employees_request_units[i] if model.average > model.employees_percents[
        i] and not model.already_assigned_in_day({Indices.EMP_I: i, Indices.DAY: indices[Indices.DAY]}) else float(
        "-inf")) for i in range(model.employees_n)]
    return Model.arg_n_max(model.shifts_emp_n[indices[Indices.SHIFT]], lst)


# Choose the employee whose assignment will bring him the most benefit.
def chooser5(model, indices):
    lst = [(model.employees_percents[i] + model.requests[i][indices[Indices.DAY]][indices[Indices.SHIFT]] *
            model.employees_request_units[i] if not model.already_assigned_in_day(
        {Indices.EMP_I: i, Indices.DAY: indices[Indices.DAY]}) else float("-inf")) for i in range(model.employees_n)]
    return Model.arg_n_max(model.shifts_emp_n[indices[Indices.SHIFT]], lst)


def main():
    # model = Model(EMPLOYEES_N, req_example, chooser3, SHIFTS_EMP_N)
    # print(model.make_assignments())
    # model.print_percentages()

    for chooser in [chooser1, chooser2, chooser3, chooser4, chooser5]:
        model = Model(EMPLOYEES_N, req_example, chooser, SHIFTS_EMP_N)
        print(model.make_assignments())


if __name__ == '__main__':
    main()
