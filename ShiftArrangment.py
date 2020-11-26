from __future__ import print_function
from ortools.sat.python import cp_model
import pandas as pd
import statistics as st
from pandas.tests.io.excel.test_xlsxwriter import xlsxwriter
import models

# This program tries to find optimal and fair assignments of employees to shifts
def main():
    num_employee = int(input("Please enter the number of employees:\n"))
    num_shifts = int(input("Please enter the number of shifts:\n"))
    num_employees_per_shift = []
    print("Please enter the number of employees of shifts:")
    for i in range(num_shifts):
        num_employees_per_shift.append(int(input()))
    num_days = int(input("Please enter the number of days:\n"))
    allocation_method = int(input("Please enter the allocation methods:\n"))
    all_employees = range(num_employee)
    all_shifts = range(num_shifts)
    all_days = range(num_days)
    choosers = [models.chooser1,models.chooser2, models.chooser3, models.chooser4, models.chooser5]

    data = pd.read_excel(r'Requests.xlsx')
    df = pd.DataFrame(data)
    shift_req_day_t = []
    shift_req_week_t = []
    shift_requests = []
    for i, row in df.iterrows():
        for j in range(num_days):
            for g in range(num_shifts):
                shift_req_day_t.append(row[chr(ord('A') + g) + str(j + 1)])
            shift_req_day = shift_req_day_t[:]
            shift_req_week_t.append(shift_req_day)
            shift_req_day_t.clear()
        shift_req_week = shift_req_week_t[:]
        shift_requests.append(shift_req_week)
        shift_req_week_t.clear()

    if allocation_method <= 5:

        ex_model = models.Model(num_employee, shift_requests, num_days, num_shifts, choosers[allocation_method - 1], num_employees_per_shift)
        assginments = ex_model.make_assignments()

    else:
        model = cp_model.CpModel()
        shifts = {}
        for n in all_employees:
            for d in all_days:
                for s in all_shifts:
                    shifts[(n, d, s)] = model.NewBoolVar('shift_n%id%is%i' % (n, d, s))

        for d in all_days:
            for e in range(len(num_employees_per_shift)):
                model.Add(sum(shifts[(n, d, e)] for n in all_employees) == num_employees_per_shift[e])

        for n in all_employees:
            for d in all_days:
                model.Add(sum(shifts[(n, d, s)] for s in all_shifts) <= 1)

        if allocation_method == 6:
            model.Maximize(sum(
                shift_requests[n][d][s] * shifts[(n, d, s)] for n in all_employees for d in all_days for s in all_shifts))
            solver = cp_model.CpSolver()
            solver.Solve(model)
            best_solver = solver

        if allocation_method == 7:
            for i in range(num_shifts * num_days):
                for n in all_employees:
                    model.Add(sum(shift_requests[n][d][s] * shifts[(n, d, s)] for d in all_days for s in all_shifts) >= i)

                model.Maximize(sum(
                    shift_requests[n][d][s] * shifts[(n, d, s)] for n in all_employees for d in all_days for s in
                    all_shifts))
                solver = cp_model.CpSolver()
                solver.Solve(model)
                solver_status = str(solver.ResponseStats())
                if "INFEASIBLE" in solver_status:
                    break
                else:
                    best_solver = solver

    workbook = xlsxwriter.Workbook('Results.xlsx')
    worksheet = workbook.add_worksheet()

    assign_employees = ""
    counters = [0] * num_employee
    for d in all_days:
        worksheet.write(0, d + 1, 'Day ' + str(d + 1))

    for s in all_shifts:
        worksheet.write(s + 1, 0, 'Shift ' + str(chr(ord('A') + s)))

    if allocation_method > 5:
        for d in all_days:
            for s in all_shifts:
                for n in all_employees:
                    if best_solver.Value(shifts[(n, d, s)]) == 1:
                        assign_employees += str(n + 1) + ", "
                        counters[n] += shift_requests[n][d][s] - 1
                worksheet.write(s + 1, d + 1, assign_employees[:-2])
                assign_employees = ""
        workbook.close()

    else:
        for d in all_days:
            for s in all_shifts:
                for n in assginments[d][s]:
                        assign_employees += str(n) + ", "
                        counters[n] += shift_requests[n][d][s] - 1
                worksheet.write(s + 1, d + 1, assign_employees[:-2])
                assign_employees = ""
        workbook.close()

    # Statistics.
    print()
    print('Statistics')
    print('  - Employees satisfaction status :')

    Total_percentage = []
    for i in range(len(counters)):
        percentage = (counters[i] / ((num_shifts - 1) * num_days)) * 100
        print('     Employee ' + str(i + 1) + ' is ' + str(percentage) + '% Statisfied')
        Total_percentage.append(percentage)

    print('  - Employees median satisfaction status : ' + str(st.median(Total_percentage)) + '% Statisfied')


if __name__ == '__main__':
    main()
