from ortools.linear_solver import pywraplp
from django.shortcuts import render

def optimize(bottle, dose, work_time, vaccine_time, teams):
    solver = pywraplp.Solver.CreateSolver('SCIP')

    infinity = solver.infinity()
    x = solver.IntVar(0.0, infinity, 'x')

    solver.Add((bottle/dose) * x <= (work_time/vaccine_time) * teams)

    solver.Maximize((bottle/dose) * x)

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        return [True, int(solver.Objective().Value()), int(x.solution_value())]
    else:
        return [False]

def index(request):
    context = {}
    return render(request, 'vaccine/index.html', context)

def form(request):
    context = {}
    return render(request, 'vaccine/form.html', context)

def result(request):
    context = {}
    if request.method == 'POST':
        vaccine_quantity = request.POST.get('vaccine_quantity')
        vaccine_dose = request.POST.get('vaccine_dose')
        work_time = request.POST.get('work_time')
        vaccine_time = request.POST.get('vaccine_time')
        teams = request.POST.get('teams')

        listOfParameters = []
        global hasErrors
        hasErrors = False
        listOfParameters.append({'name': 'vaccine_quantity', 'value': vaccine_quantity})
        listOfParameters.append({'name': 'vaccine_dose', 'value': vaccine_dose})
        listOfParameters.append({'name': 'work_time', 'value': work_time})
        listOfParameters.append({'name': 'vaccine_time', 'value': vaccine_time})
        listOfParameters.append({'name': 'teams', 'value': teams})
        errorContext = {'hasErrorText': True}
        for parameter in listOfParameters:
            if(parameter['value'] == ''):
                hasErrors = True
                errorContext[parameter['name']] = parameter['value']
                errorContext[parameter['name'] + 'ErrorText'] = 'Insira um valor para continuar'
            else:
                errorContext[parameter['name']] = parameter['value']
                errorContext[parameter['name'] + 'ErrorText'] = ''
        
        if hasErrors:
            return render(request, 'vaccine/form.html', errorContext)

        work_time_splited = work_time.split(':')
        work_time_in_minutes = (int(work_time_splited[0]) * 60) + int(work_time_splited[1])
        vaccine_time_splited = vaccine_time.split(':')
        vaccine_time_in_minutes = (int(vaccine_time_splited[0]) * 60) + int(vaccine_time_splited[1])

        resultList = optimize(float(vaccine_quantity), float(vaccine_dose), work_time_in_minutes, vaccine_time_in_minutes, int(teams))
        print(resultList)
        if resultList[0]:
            context.update({'people': resultList[1], 'vaccines': resultList[2]})
        else:
            context.update({'people': 0, 'vaccines': 0})
    
    return render(request, 'vaccine/result.html', context)


