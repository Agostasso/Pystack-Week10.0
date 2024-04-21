from django.shortcuts import render, redirect
from .models import Especialidades, DadosMedicos, is_medico, DatasAbertas
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime, timedelta
from paciente.models import Consulta, Documento


# Create your views here.

def cadastro_medico(request):

    
    if is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Você já é medico')
        return redirect('/medicos/abrir_horario')# vai dar erro

    if request.method == "GET":
        especialidades = Especialidades.objects.all()
        
        return render(request, 'cadastro_medico.html', {'especialidades': especialidades, 'is_medico':is_medico(request.user)})
    
    elif request.method == "POST":
        crm = request.POST.get('crm')
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        cim = request.FILES.get('cim')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')
        especialidade = request.POST.get('especialidade')
        descricao = request.POST.get('descricao')
        valor_consulta = request.POST.get('valor_consulta')

        dados_medico = DadosMedicos(

            crm=crm,
            nome=nome,
            cep=cep,
            rua=rua,
            bairro=bairro,
            numero=numero,
            rg=rg,
            cedula_identidade_medica = cim,
            foto=foto,
            especialidade_id=especialidade,
            descricao = descricao,
            valor_consulta = valor_consulta,
            user=request.user
        )
       
        dados_medico.save()
        messages.add_message(request, constants.SUCCESS, 'cadastro realizado com sucesso')

        return redirect('/medico/abrir_horario') # proxima aula

def abrir_horario(request):

    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente medicos podem abrir horarios')
        return redirect("/usuarios/sair")

    if request.method == "GET":
        dados_medicos = DadosMedicos.objects.get(user=request.user)
        datas_abertas = DatasAbertas.objects.filter(user=request.user)
        print(datas_abertas)
        return render(request, 'abrir_horario.html', {'dados_medicos':dados_medicos, 'datas_abertas': datas_abertas, 'is_medico':is_medico(request.user)})
    
    elif request.method =="POST":
        data = request.POST.get('data')
        data_formatada = datetime.strptime(data, '%Y-%m-%dT%H:%M')

        if data_formatada <= datetime.now():
            messages.add_message(request, constants.WARNING, 'A data nao pode ser anterior a data actual')
            return redirect('/medico/abrir_horario')

        horario_abrir = DatasAbertas(
            data = data,
            user = request.user
        )  
        horario_abrir.save()

        messages.add_message(request, constants.SUCCESS, 'Horario cadastrado com sucesso')

        return redirect('/medico/abrir_horario')

def consultas_medico(request):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')

    hoje = datetime.now().date()
    consultas_hoje = Consulta.objects.filter(data_aberta__user=request.user).filter(data_aberta__data__gte=hoje).filter(data_aberta__data__lt=hoje + timedelta(days=1))
    consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values('id'))
    return render(request, 'consultas_medico.html', {'consultas_hoje': consultas_hoje, 'consultas_restantes': consultas_restantes, 'is_medico': is_medico(request.user)})

def consulta_area_medico(request, id_consulta):

    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente medicos podem abrir horarios')
        return redirect('/usuarios/sair')

    if request.method == 'GET':
        consulta = Consulta.objects.get(id=id_consulta)
        documentos = Documento.objects.filter(consulta=consulta)

        return render(request, 'consulta_area_medico.html', {'consulta': consulta, 'is_medico': is_medico(request.user), 'documentos':documentos})
    
    elif request.method == "POST":
        consulta = Consulta.objects.get(id=id_consulta)
        link = request.POST.get('link')

        if consulta.status == 'C':
            messages.add_message(request, constants.WARNING, 'Essa consulta ja foi cancelada.')
            return redirect(f'/medico/consulta_area_medico/{id_consulta}')
        elif consulta.status == "F":
            messages.add_message(request, constants.WARNING, 'Essa consulta ja foi Finalizada')
            return redirect(f'/medico/consulta_area_medico/{id_consulta}')
        
        
        consulta.link = link
        consulta.status ="I"
        consulta.save()
        messages.add_message(request, constants.SUCCESS, 'Consulta iniciada')
        return redirect(f'/medico/consulta_area_medico/{id_consulta}')
          
    
       
def finalizar_consulta(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente medicos podem abrir horarios')
        return redirect('/usuarios/sair')
  
    consulta = Consulta.objects.get(id=id_consulta)
    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.ERROR, 'essa consulta nao e sua!')
        return redirect(f'/medico/consulta_area_medico/{id_consulta}')

    consulta.status = 'F'
    consulta.save()
    return redirect(f'/medico/consulta_area_medico/{id_consulta}')
    
def add_documento(request, id_consulta):
    if not is_medico(request.user):
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')

    consulta = Consulta.objects.get(id=id_consulta)

    if consulta.data_aberta.user != request.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua!')
        return redirect(f'/medico/consulta_area_medico/{id_consulta}')


    titulo = request.POST.get('titulo')
    documento = request.FILES.get('documento')
    if not documento:
        messages.add_message(request, constants.WARNING, 'Adicione o documento.')
        return redirect(f'/medico/consulta_area_medico/{id_consulta}')
    documento = Documento(
    consulta=consulta,
    titulo=titulo,
    documento=documento
    )
    documento.save()
    messages.add_message(request, constants.SUCCESS, 'Documento enviado com sucesso!')
    return redirect(f'/medico/consulta_area_medico/{id_consulta}')
            

