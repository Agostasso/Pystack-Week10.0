from django.shortcuts import render, redirect
from django.http import HttpResponse
from medico.models import DadosMedicos, Especialidades, DatasAbertas, is_medico
from datetime import datetime
from .models import Consulta, Documento
from django.contrib import messages
from django.contrib.messages import constants

def home(request):
    if request.method == "GET":
        medico_filtrar = request.GET.get('medico')
        especialidade_filtrar = request.GET.getlist('especialidades')
        medicos = DadosMedicos.objects.all()
        

        if medico_filtrar:
            medicos = medicos.filter(nome__icontains=medico_filtrar)
        
        if especialidade_filtrar:
            medicos = medicos.filter(especialidade_id__in=especialidade_filtrar)
        
        especialidades =Especialidades.objects.all()
        return render(request, 'home.html', {'medicos': medicos, 'especialidades':especialidades, 'is_medico':is_medico(request.user)})

def escolher_horario(request, id_dados_medicos):
    if request.method=="GET":
        medico = DadosMedicos.objects.get(id=id_dados_medicos)
        datas_abertas = DatasAbertas.objects.filter(user=medico.user).filter(data__gte=datetime.now()).filter(agendado=False)
       
        return render(request, 'escolher_horario.html', {'medico':medico, 'datas_abertas':datas_abertas, 'is_medico':is_medico(request.user)})

def agendar_horario(request, id_data_aberta):
    if request.method == "GET":
        data_aberta = DatasAbertas.objects.get(id=id_data_aberta)
        horario_agendado = Consulta(
        paciente=request.user,
        data_aberta=data_aberta
        )
        horario_agendado.save()  

        #TODO: Sugestão Tornar atomico
        data_aberta.agendado = True
        data_aberta.save()
        messages.add_message(request, constants.SUCCESS, 'Horário agendado com sucesso.')
        return redirect('/paciente/minhas_consultas/')  


def minhas_consultas(request):

    if request.method == "GET":
        #TODO: desenvolver filtros
        minhas_consultas = Consulta.objects.filter(paciente=request.user).filter(data_aberta__data__gte=datetime.now())
        return render(request, 'minhas_consultas.html', {'minhas_consultas': minhas_consultas, 'is_medico':is_medico(request.user)})

def consulta(request, id_consulta):
    if request.method == 'GET':
        consulta = Consulta.objects.get(id=id_consulta)
        dado_medico = DadosMedicos.objects.get(user=consulta.data_aberta.user)
        documentos = Documento.objects.filter(consulta =  consulta)
        return render(request, 'consulta.html', {'consulta': consulta, 'dado_medico': dado_medico, 'is_medico': is_medico(request.user), 'documentos':documentos})

#Canncela consulta TPC
#Fazer a validacao de seguranca nos restantes pontos do codigo
# Dashboard