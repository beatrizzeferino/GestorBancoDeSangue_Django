from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Utilizador, Posto, Hospital, Dador, Doacao, StockSangue, PedidoHospital
from django.utils import timezone
from django.db.models import Count, Q, Sum, F
from django.db.models.functions import TruncMonth, ExtractMonth
import json
import datetime
from django.db import transaction


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            try:

                perfil = user.utilizador
                
                if perfil.tipo == 'ADMIN':
                    return redirect('home_admin')
                elif perfil.tipo == 'POSTO':
                    return redirect('home_posto')
                elif perfil.tipo == 'HOSPITAL':
                    return redirect('home_hospital') 
                else:
                    
                    return redirect('/admin/')
            except:
                return redirect('/admin/')
            
        else:
            messages.error(request, "Username ou Password incorretos.")

    return render(request, 'autenticacao.html')


# ///////////////////////// Administrador \\\\\\\\\\\\\\\\\\\\\\\

@login_required #so tem acesso a esta view se tiver feito login
@user_passes_test(lambda u: u.utilizador.tipo == 'ADMIN') #para cada tipo de view so determinado tipo de utilizador pode visualiza-la
def home_admin(request):
    return render(request, 'admin_home.html')

#-------------Criar Admin-----------------

@login_required
@user_passes_test(lambda u: u.utilizador.tipo == 'ADMIN')
@transaction.atomic #como e criado um user e um utilizador garante que ou sao ambos criados ou nenhum
def menu_add_admin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists():
                messages.error(request, "Este ID de administrador já existe.")
                return render(request, 'menu_add_admin.html')
        
        novo_user= User.objects.create_user(username=username, password=password, email=email)

        Utilizador.objects.create(user=novo_user,tipo='ADMIN')

        messages.success(request, "Novo administrador criado com sucesso!") #isto depois pode é usado no template para imprimir a mensagem
        return redirect('home_admin')
    return render(request, 'menu_add_admin.html')


#--------------Postos---------------------------------

@login_required
@user_passes_test(lambda u: u.utilizador.tipo == 'ADMIN')
def menu_postos(request):
    return render(request, 'menu_postos.html')

@login_required
@user_passes_test(lambda u: u.utilizador.tipo == 'ADMIN')
@transaction.atomic #como cria um user, um posto e um utilizador se algum destes falhar garante que nenhuma operacao é feita
def criar_posto(request):
    if request.method == 'POST':
        nome=request.POST.get('nome')
        nif=request.POST.get('nif')
        contacto=request.POST.get('contacto')
        morada=request.POST.get('morada')
        
        username=request.POST.get('username')
        password=request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Este ID de utilizador já existe.")
            return render(request, 'criar_posto.html')

        if Posto.objects.filter(nif=nif).exists():
            messages.error(request, "Já existe um posto registado com este NIF.")
            return render(request, 'criar_posto.html')
        
        p= Posto.objects.create(nome=nome, nif=nif, contacto=contacto, morada=morada)
        u= User.objects.create_user(username=username, password=password)
        Utilizador.objects.create(user=u, tipo='POSTO', posto=p)

        messages.success(request, "Posto criado com sucesso!")
        return redirect('menu_postos')
    
    return render(request, 'criar_posto.html')

@login_required
@user_passes_test(lambda u: u.utilizador.tipo == 'ADMIN')
def selecionar_posto_para_atualizar(request):
    query = request.GET.get('q')

    if query:
        postos = Posto.objects.filter(nome__icontains=query) | Posto.objects.filter(nif__icontains=query) #um ou outro (or) e ignora maiusculas e minusculas
    else:
        postos = Posto.objects.all()

    return render(request, 'selecionar_posto_atualizar.html', {'postos': postos})

@login_required
@user_passes_test(lambda u: u.utilizador.tipo == 'ADMIN')
def atualizar_posto(request, posto_id):
    # Procura o posto ou dá erro 404 se não existir
    posto = get_object_or_404(Posto, id=posto_id)
    
    if request.method == "POST":
        try:
            nome = request.POST.get('nome')
            if nome: 
                posto.nome = nome
            novo_nif = request.POST.get('nif')
            if novo_nif and novo_nif!=posto.nif:
                if Posto.objects.filter(nif=novo_nif).exclude(id=posto.id).exists():
                    messages.error(request, f"Erro: O NIF {novo_nif} já está registado noutro posto.")
                posto.nif = novo_nif         
            contacto = request.POST.get('contacto')
            if contacto:
                posto.contacto = contacto        
            morada = request.POST.get('morada')
            if morada:
                posto.morada = morada
            posto.save()

            messages.success(request, f"Posto '{posto.nome}' atualizado com sucesso!")

            return redirect('menu_postos')

        except Exception as e:
            messages.error(request, f"Erro ao atualizar unidade: {e}")

    return render(request, 'atualizar_posto.html', {'posto': posto})


@login_required
@user_passes_test(lambda u: u.utilizador.tipo == 'ADMIN')
def procurar_posto(request):
    posto_encontrado =None
    query= request.GET.get('id_ou_nif')

    if query:
        posto_encontrado = Posto.objects.filter(nif=query).first()
        if not posto_encontrado and query.isdigit():
            posto_encontrado = Posto.objects.filter(id=query).first()
        if not posto_encontrado:
            messages.error(request, "Nenhum posto encontrado com esse ID ou NIF.")

    return render(request, 'procurar_posto.html', {'posto': posto_encontrado, 'procurou': True if query else False}) 

@login_required
@user_passes_test(lambda u: u.utilizador.tipo == 'ADMIN')
def listar_postos(request):
    todos_postos=Posto.objects.all()
    return render(request, 'listar_postos.html', {'postos': todos_postos})

#-------------------Hospitais---------------------------
@login_required
@user_passes_test(lambda u: u.utilizador.tipo == 'ADMIN')
def menu_hospitais(request):
    return render(request, 'menu_hospitais.html')

@login_required
@user_passes_test(lambda u: u.utilizador.tipo == 'ADMIN')
@transaction.atomic #como cria um user, um hospital e um utilizar se algum destes falhar garante que nenhuma operacao é feita
def criar_hospital(request):
    if request.method == 'POST':
        nome=request.POST.get('nome')
        nif=request.POST.get('nif')
        contacto=request.POST.get('contacto')
        morada=request.POST.get('morada')
        
        username=request.POST.get('username')
        password=request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Este ID de utilizador já existe.")
            return render(request, 'criar_hospital.html')

        h= Hospital.objects.create(nome=nome, nif=nif, contacto=contacto, morada=morada)
        u= User.objects.create_user(username=username, password=password)
        Utilizador.objects.create(user=u, tipo='HOSPITAL', hospital=h)

        messages.success(request, "Hospital criado com sucesso!")
        return redirect('menu_hospitais')
    
    return render(request, 'criar_hospital.html')

@login_required
@user_passes_test(lambda u: u.utilizador.tipo == 'ADMIN')
def selecionar_hospital_para_atualizar(request):
    query = request.GET.get('q')

    if query:
        hospitais = Hospital.objects.filter(nome__icontains=query) | Hospital.objects.filter(nif__icontains=query)
    else:
        hospitais = Hospital.objects.all()

    return render(request, 'selecionar_hospital_atualizar.html', {'hospitais': hospitais})

@login_required
@user_passes_test(lambda u: u.utilizador.tipo == 'ADMIN')
def atualizar_hospital(request, hospital_id):
    # Procura o hospital ou dá erro 404 se não existir
    hospital = get_object_or_404(Hospital, id=hospital_id)
    
    if request.method == "POST":
        try:
            nome = request.POST.get('nome')
            if nome: 
                hospital.nome = nome

            novo_nif = request.POST.get('nif')
            if novo_nif and novo_nif != hospital.nif:
                if Hospital.objects.filter(nif=novo_nif).exclude(id=hospital.id).exists():
                    messages.error(request, f"Erro: O NIF {novo_nif} já está registado noutro hospitala.")
                    return render(request, 'atualizar_hospital.html', {'hospital': hospital})
                hospital.nif = novo_nif         

            hospital.contacto = request.POST.get('contacto')
            hospital.morada = request.POST.get('morada')

            hospital.save()
            messages.success(request, f"Hospital '{hospital.nome}' atualizado com sucesso!")
            return redirect('menu_hospitais')

        except Exception as e:
            messages.error(request, f"Erro ao hospital: {e}")

    return render(request, 'atualizar_hospital.html', {'hospital': hospital})


@login_required
@user_passes_test(lambda u: u.utilizador.tipo == 'ADMIN')
def procurar_hospital(request):
    hospital_encontrado =None
    query= request.GET.get('id_ou_nif')

    if query:
        hospital_encontrado = Hospital.objects.filter(nif=query).first()
        if not hospital_encontrado and query.isdigit():
            hospital_encontrado = Hospital.objects.filter(id=query).first()
        if not hospital_encontrado:
            messages.error(request, "Nenhum hospital encontrado com esse ID ou NIF.")

    return render(request, 'procurar_hospital.html', {'hospital': hospital_encontrado, 'procurou': True if query else False})

@login_required
@user_passes_test(lambda u: u.utilizador.tipo == 'ADMIN')
def listar_hospitais(request):
    todos_hospitais=Hospital.objects.all()
    return render(request, 'listar_hospitais.html', {'hospitais': todos_hospitais})

#-------------------Stock-----------------
@login_required
@user_passes_test(lambda u: u.utilizador.tipo in ['ADMIN', 'HOSPITAL'])
def menu_stock(request): 
    todos_stocks= StockSangue.objects.all().order_by('tipoSangue', 'componente')
    tipo_user = request.user.utilizador.tipo

    alertas_abaixo_minimo=[]
    

    for s in todos_stocks:
        if s.quantidade < s.limiteMinimo:
            alertas_abaixo_minimo.append(s)

    
    
    return render(request, 'menu_stock.html', {'stocks': todos_stocks, 'alertas_abaixo_minimo': alertas_abaixo_minimo, 'tipo_user': tipo_user})

#------------------Doacoes----------------
'''@login_required
def menu_doacoes(request):
    return render(request, 'menu_doacoes.html')'''

@login_required #posto só consegue ver as doações feitas nesse posto
@user_passes_test(lambda u: u.utilizador.tipo in ['ADMIN', 'POSTO'])
def consultar_doacoes(request):
    doacoes=Doacao.objects.none()
    tipo_user = request.user.utilizador.tipo

    modo=request.GET.get('modo') #modo: dador, tipo , tudo

    query_nif =request.GET.get('id_ou_nif')
    query_tipo =request.GET.get('tipo_sangue')

    if tipo_user == 'ADMIN':
        base_doacoes = Doacao.objects.all()
    else:
        # O Posto só vê as doações do seu posto
        base_doacoes = Doacao.objects.filter(posto=request.user.utilizador.posto)
    
    if modo== 'dador':
        if query_nif:
            dador= Dador.objects.filter(nif=query_nif).first()
            if not dador and query_nif.isdigit():
                dador=Dador.objects.filter(id=query_nif).first()

            if dador:
                doacoes= base_doacoes.filter(dador=dador).order_by('-data') #ordena as doacoes por ordem decrescente das datas
            else:
                messages.error(request, "Dador não encontrado.")
    elif modo=='tipo':
        if query_tipo:
            doacoes= base_doacoes.filter(dador__tipoSangue=query_tipo).order_by('-data')

    elif modo=='tudo':
        doacoes=base_doacoes.order_by('-data')

    return render(request, 'consultar_doacoes.html', {'doacoes': doacoes, 'modo': modo, 'query_nif': query_nif, 'query_tipo': query_tipo, 'tipo_user': tipo_user})
#--------------------Pedidos---------------------------

@login_required #permite no caso do hospital consultar apenas os pedidos desse hospital
@user_passes_test(lambda u: u.utilizador.tipo in ['ADMIN', 'HOSPITAL'])
def consultar_pedidos_hospital(request):
    tipo_user = request.user.utilizador.tipo
    if tipo_user == 'ADMIN':
        pedidos = PedidoHospital.objects.all().order_by('-dataPedido')
    else:
        pedidos = PedidoHospital.objects.filter(
            hospital=request.user.utilizador.hospital
        ).order_by('-dataPedido')

    pedidos_aprovados = pedidos.filter(estadoPedido='A')
    pedidos_pendentes = pedidos.filter(estadoPedido='P')
    pedidos_rejeitados = pedidos.filter(estadoPedido='R')

    return render(request, 'consultar_pedidos.html', {
        'tipo_user': tipo_user,
        'pedidos_aprovados': pedidos_aprovados,
        'pedidos_pendentes': pedidos_pendentes,
        'pedidos_rejeitados': pedidos_rejeitados,
    })

#---------------------Relatorios-------------------------

@login_required
@user_passes_test(lambda u: u.utilizador.tipo == 'ADMIN')
def gerar_relatorios(request):
    tipo = request.GET.get('tipo')
    ano = request.GET.get('ano', datetime.datetime.now().year)

    context = {
        'tipo': tipo,
        'ano_selecionado': ano,
        'dados_tabela': [],
        'chart_labels': [],
        'chart_valores': [],
        'listagens_detalhe': []
    }


    if tipo == 'dadores_ativos':
        ativos = Dador.objects.filter(ativo=True).count()
        inativos = Dador.objects.filter(ativo=False).count()

        context['dados_tabela'] = [
            {'label': 'Dadores Ativos', 'valor': ativos},
            {'label': 'Dadores Inativos', 'valor': inativos},
            {'label': 'Total', 'valor': ativos + inativos}
        ]
        context['chart_labels'] = ['Ativos', 'Inativos']
        context['chart_valores'] = [ativos, inativos]

        context['listagens_detalhe'] = [
            {'titulo': 'Dadores Ativos', 'lista': Dador.objects.filter(ativo=True)},
            {'titulo': 'Dadores Inativos', 'lista': Dador.objects.filter(ativo=False)}
        ]
    
    elif tipo == 'dadores_sangue':
        # 1. Definir todos os tipos possíveis (conforme o teu Dador.TIPO_SANGUE)
        todos_tipos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

        context['dados_tabela'] = []
        context['listagens_detalhe'] = []
        context['chart_labels'] = []
        context['chart_valores'] = []

        for t in todos_tipos:
            dadores_do_tipo = Dador.objects.filter(tipoSangue=t)
            contagem = dadores_do_tipo.count()

            context['dados_tabela'].append({'label': t, 'valor': contagem})
            context['chart_labels'].append(t)
            context['chart_valores'].append(contagem)

            context['listagens_detalhe'].append({
                'titulo': f'Dadores Tipo {t}',
                'lista': dadores_do_tipo,
                'tipo_slug': t.replace('+', 'pos').replace('-', 'neg')
            })

    elif tipo == 'pedidos_estado':
        context['dados_tabela'] = [
            {'label': 'Aprovados', 'valor': PedidoHospital.objects.filter(estadoPedido='A').count()},
            {'label': 'Pendentes', 'valor': PedidoHospital.objects.filter(estadoPedido='P').count()},
            {'label': 'Rejeitados', 'valor': PedidoHospital.objects.filter(estadoPedido='R').count()},
        ]

        context['chart_labels'] = [d['label'] for d in context['dados_tabela']]
        context['chart_valores'] = [d['valor'] for d in context['dados_tabela']]


        context['listagens_detalhe'] = [
            {
                'titulo': 'Pedidos Aprovados', 
                'lista': PedidoHospital.objects.filter(estadoPedido='A')
            },
            {
                'titulo': 'Pedidos Pendentes', 
                'lista': PedidoHospital.objects.filter(estadoPedido='P')
            },
            {
                'titulo': 'Pedidos Rejeitados', 
                'lista': PedidoHospital.objects.filter(estadoPedido='R')
            }
        ]


    elif tipo == 'doacoes_mes':
        meses_nome = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

        doacoes = Doacao.objects.filter(data__year=ano)\
            .annotate(mes=ExtractMonth('data'))\
            .values('mes').annotate(total=Count('id')).order_by('mes') #cria uma variavel mes e depois por mes conta quantas doacoes tem desse mes

        doacoes_dict = {d['mes']: d['total'] for d in doacoes}

        for i, nome in enumerate(meses_nome, 1):
            qtd = doacoes_dict.get(i, 0)
            context['dados_tabela'].append({'label': nome, 'valor': qtd})
            context['chart_labels'].append(nome)
            context['chart_valores'].append(qtd)

    elif tipo == 'stock_geral':
        stock = StockSangue.objects.all().order_by('tipoSangue')
        for item in stock:
            context['dados_tabela'].append({
                'tipo': item.tipoSangue,
                'componente': item.get_componente_display,
                'qtd': item.quantidade
            })
            context['chart_labels'].append(f"{item.tipoSangue} ({item.componente})")
            context['chart_valores'].append(item.quantidade)

    elif tipo == 'stock_critico':
        criticos = StockSangue.objects.filter(quantidade__lt=F('limiteMinimo')) 
        for item in criticos:
            context['dados_tabela'].append({
                'tipo': item.tipoSangue,
                'componente': item.get_componente_display,
                'qtd': item.quantidade
            })

    return render(request, 'gerar_relatorio.html', context)
    

#----------------Outros-----------------------

@login_required
@user_passes_test(lambda u: u.utilizador.tipo == 'ADMIN')
def menu_outros(request):
    return render(request, 'menu_outros.html')

@login_required
@user_passes_test(lambda u: u.utilizador.tipo in ['ADMIN', 'POSTO'])
def adicionar_dador(request):
    tipo_user = request.user.utilizador.tipo
    if request.method == 'POST':
        nome = request.POST.get('nome')
        nif = request.POST.get('nif')
        contacto = request.POST.get('contacto')
        data_nasc = request.POST.get('dataNascimento')
        tipo_sangue = request.POST.get('tipoSangue')
        sexo = request.POST.get('sexo')
        peso = float(request.POST.get('peso', 0))
        medicacao = request.POST.get('medicacao') == 'on' #checkboxes
        tatuagem = request.POST.get('tatuagem') == 'on'
        piercing = request.POST.get('piercing') == 'on'
        doente = request.POST.get('doente') == 'on'

        if Dador.objects.filter(nif=nif).exists():
            messages.error(request, "Já existe um dador com este NIF.")
            return render(request, 'adicionar_dador.html', {'tipo_user': tipo_user})
        try:
            Dador.objects.create(
                nome=nome,
                nif=nif,
                contacto=contacto,
                dataNascimento=data_nasc,
                tipoSangue=tipo_sangue,
                sexo=sexo,
                peso=peso,
                medicacao=medicacao,
                tatuagem=tatuagem,
                piercing=piercing,
                doente=doente,
                ativo=True)
            messages.success(request, f"Dador {nome} registado com sucesso!")
            
            if tipo_user == 'ADMIN':
                return redirect('menu_outros')
            elif tipo_user == 'POSTO':
                return redirect('home_posto')
            else:
                return redirect('login')
        
        except Exception as e:
            messages.error(request, f"Erro ao registar dador: {e}")
    
    return render(request, 'adicionar_dador.html', {'tipo_user': tipo_user})

def verificar_pedidos_pendentes(tipo_sangue_doado):
    pedidos_pendentes= PedidoHospital.objects.filter(
        tipo_sangue=tipo_sangue_doado,
        estadoPedido= 'P'
        ).order_by('dataPedido') #ordenado pela data do pedido para dar prioridade a quem pediu primeiro

    for pedido in pedidos_pendentes:
        stock_item=StockSangue.objects.select_for_update().filter( #garante que cada linha de stock é tratada de forma isolada, fica trancada enquanto está a ser usada, evitando que 2 processos aprovem pedidos simultaneos para o mesmo volume de sangue
            tipoSangue= tipo_sangue_doado,
            componente=pedido.componente
        ).first()

        if stock_item and stock_item.quantidade>= pedido.quantidade:
            pedido.estadoPedido='A'
            pedido.save()

            stock_item.quantidade = F('quantidade') - pedido.quantidade #altera valor na base de dados
            stock_item.save()

@login_required
@user_passes_test(lambda u: u.utilizador.tipo in ['ADMIN', 'POSTO'])
@transaction.atomic #garante que a doacao e aumento do stock são atómicos, ou acontece tudo ou não acontece nada
def adicionar_doacao(request):
    tipo_user = request.user.utilizador.tipo
    postos = Posto.objects.all() if tipo_user == 'ADMIN' else None
    if request.method=='POST':
        nif_dador= request.POST.get('nif')
        quantidade= int(request.POST.get('quantidade', 0))                          

        if request.user.utilizador.tipo == 'ADMIN':
            posto_id = request.POST.get('posto')
            posto_selecionado = Posto.objects.filter(id=posto_id).first()
        else:
            posto_selecionado = request.user.utilizador.posto

        data_doacao=timezone.now()

        dador= Dador.objects.filter(nif=nif_dador).first()

        if not dador:
            messages.error(request, f"Dador com nif {nif_dador} não foi encontrado.")
            return render(request, 'adicionar_doacao.html', {'postos': postos, 'tipo_user': tipo_user, 'hoje': timezone.now().date().isoformat()})
        
        if not dador.ativo:
            messages.error(request, f"O dador {dador.nome} está inativo para a doação de sangue.")
            return render(request, 'adicionar_doacao.html', {'postos': postos, 'tipo_user': tipo_user, 'hoje': timezone.now().date().isoformat()})

        if not dador.aptidaoAtual:
            messages.error(request, f"O dador {dador.nome} não está apto para doar sangue neste momento.")
            return render(request, 'adicionar_doacao.html', {'postos': postos, 'tipo_user': tipo_user, 'hoje': timezone.now().date().isoformat()})
        
        if not posto_selecionado:
            messages.error(request, "Erro: Posto de recolha não identificado.")
            return render(request, 'adicionar_doacao.html', {'postos': postos, 'tipo_user': tipo_user, 'hoje': timezone.now().date().isoformat()})
        
        try:
            componentes = ['GV', 'PL', 'PQ']
            
            stocks_para_atualizar= StockSangue.objects.select_for_update().filter( #bloqueamos todos os componente de stock deste tipo de sangue para de momento mais ninguem conseguir atualizar
                tipoSangue=dador.tipoSangue, 
                componente__in=componentes 
            )
               
            for stock_item in stocks_para_atualizar:
                if (stock_item.quantidade + quantidade) > stock_item.limiteMaximo:
                    messages.error(request, 
                        f"Doação cancelada! Limite de {stock_item.limiteMaximo} ml excedido."
                    )
                    return render(request, 'adicionar_doacao.html', {'postos': postos, 'tipo_user': tipo_user})
            
            Doacao.objects.create(
                dador=dador,
                posto=posto_selecionado,
                quantidade=quantidade,
                data=data_doacao
            )

            for stock_item in stocks_para_atualizar:
                stock_item.quantidade = F('quantidade') + quantidade #altera valor na base de dados
                stock_item.save()
                stock_item.refresh_from_db() #para que a funcao seguinte saiba o novo valor, o valor real
    
            verificar_pedidos_pendentes(dador.tipoSangue)

            messages.success(request, f"A doação de {dador.nome} foi registada com sucesso!")
            if tipo_user == 'ADMIN':
                return redirect('menu_outros')
            else:
                return redirect('home_posto')
        
        except Exception as e:
            messages.error(request, f"Erro: {e}")
    
    return render(request, 'adicionar_doacao.html', {'postos': postos, 'tipo_user': tipo_user, 'hoje': timezone.now().date().isoformat()})

@login_required
@user_passes_test(lambda u: u.utilizador.tipo in ['ADMIN', 'HOSPITAL'])
@transaction.atomic
def fazer_pedido(request):
    tipo_user = request.user.utilizador.tipo
    hospitais= Hospital.objects.all() if tipo_user == 'ADMIN' else None #opcoes que apenas o administrador vai ter para decidir qual é o hospital que ta a fazer o pedido

    if request.method=='POST':
        tipo_sangue_pedido= request.POST.get('tipo_sangue')
        componente =request.POST.get('componente')
        quantidade =float(request.POST.get('quantidade', 0))

        if tipo_user == 'ADMIN':
            hospital_id = request.POST.get('hospital')
            hospital_obj = Hospital.objects.filter(id=hospital_id).first()
        else:
            hospital_obj = request.user.utilizador.hospital

        if not hospital_obj:
            messages.error(request, "Erro: Hospital não identificado.")
            return render(request, 'fazer_pedido.html', {'hospitais': hospitais, 'tipo_user': tipo_user})

        data_pedido=timezone.now()

        try:
            stock_item =StockSangue.objects.select_for_update().filter( #bloqueamos a linha do stock que o hospital quer fazer o pedido
                tipoSangue= tipo_sangue_pedido,
                componente=componente
            ).first()

            if stock_item and stock_item.quantidade >= quantidade:
                estado_final ='A'
                stock_item.quantidade = F('quantidade') - quantidade #subtracao feita na bd
                stock_item.save()
                messages.success(request, f"Pedido de {quantidade} ml de {componente} aprovado!")

            else:
                estado_final='P'
                messages.warning(request, f"Pedido de {quantidade} ml de {componente} pendente, stock insuficiente.")

            PedidoHospital.objects.create(
                hospital=hospital_obj,
                tipo_sangue=tipo_sangue_pedido,
                quantidade=quantidade,
                componente=componente,
                estadoPedido=estado_final,
                dataPedido=data_pedido
            )

            if tipo_user == 'ADMIN':
                return redirect('menu_outros')
            else:
                return redirect('home_hospital')
        
        except Exception as e:
            messages.error(request, f"Erro ao processar o pedido: {e}")
    
    return render(request, 'fazer_pedido.html', {'hospitais': hospitais, 'tipo_user': tipo_user,'hoje': timezone.now().date().isoformat()} )

@login_required
@user_passes_test(lambda u: u.utilizador.tipo in ['ADMIN', 'POSTO'])
def listar_dadores(request):
    dadores_ativos= Dador.objects.filter(ativo=True)
    dadores_inativos= Dador.objects.filter(ativo=False)

    tipo_user = request.user.utilizador.tipo

    return render(request, 'listar_dadores.html', {'dadores_ativos': dadores_ativos, 'dadores_inativos': dadores_inativos, 'tipo_user': tipo_user})

@login_required
@user_passes_test(lambda u: u.utilizador.tipo in ['ADMIN', 'POSTO'])
def procurar_dador(request):
    dador_encontrado =None
    query= request.GET.get('id_ou_nif')

    if query:
        dador_encontrado = Dador.objects.filter(nif=query).first()
        if not dador_encontrado and query.isdigit():
            dador_encontrado = Dador.objects.filter(id=query).first()
        if not dador_encontrado:
            messages.error(request, "Nenhum dador encontrado com esse ID ou NIF.")
    
    tipo_user = request.user.utilizador.tipo

    return render(request, 'procurar_dador.html', {'dador': dador_encontrado, 'procurou': True if query else False, 'tipo_user': tipo_user}) 

@login_required
@user_passes_test(lambda u: u.utilizador.tipo in ['ADMIN', 'POSTO'])
def ativar_desativar_dador(request):
        
    # Obtém o tipo de utilizador para redirecionamentos
    tipo_user = request.user.utilizador.tipo
    query = request.GET.get('id_ou_nif')

    if query:
        dador_encontrado = Dador.objects.filter(nif=query).first()
        
        if not dador_encontrado and query.isdigit():
            dador_encontrado = Dador.objects.filter(id=query).first()

        if not dador_encontrado:
            messages.error(request, "Dador não encontrado com os dados inseridos.")
        
        else:
            if not dador_encontrado.ativo:
                if not dador_encontrado.aptidaoAtual:
                    messages.error(
                        request, 
                        f"PROIBIDO: O dador {dador_encontrado.nome} está marcado como CLINICAMENTE INAPTO. "
                        "A conta não pode ser ativada enquanto a aptidão for negativa."
                    )
                    
                    if tipo_user == 'ADMIN':
                        return redirect('menu_outros')
                    else:
                        return redirect('home_posto')
                    
                    
            dador_encontrado.ativo = not dador_encontrado.ativo
            dador_encontrado.save()

            if dador_encontrado.ativo:
                estado_texto = 'ATIVADO'
                tipo_msg = messages.SUCCESS
            else:
                estado_texto = 'DESATIVADO'
                tipo_msg = messages.WARNING # Amarelo para indicar desativação

            messages.add_message(request, tipo_msg, f"Sucesso: O dador {dador_encontrado.nome} foi {estado_texto}.")

            if tipo_user == 'ADMIN':
                return redirect('menu_outros')
            else:
                return redirect('home_posto')

    return render(request, 'ativar_desativar_dador.html', {'tipo_user': tipo_user})

@login_required
@user_passes_test(lambda u: u.utilizador.tipo in ['ADMIN', 'POSTO'])
def selecionar_dador_para_atualizar(request):
    tipo_user = request.user.utilizador.tipo
    dadores_lista = Dador.objects.all().order_by('-id') 
    query = request.GET.get('q')
    if query:
        dadores_lista = dadores_lista.filter(
            Q(nome__icontains=query) | Q(nif__icontains=query)
        )
    context = {
        'tipo_user': tipo_user,
        'dadores': dadores_lista  
    }

    return render(request, 'selecionar_dador_atualizar.html', {'tipo_user': tipo_user,'dadores': dadores_lista})

@login_required
@user_passes_test(lambda u: u.utilizador.tipo in ['ADMIN', 'POSTO'])
def atualizar_dador(request, dador_id):
    # Usa get_object_or_404 para evitar erro 500 se o ID não existir
    dador = get_object_or_404(Dador, id=dador_id)
    tipo_user = request.user.utilizador.tipo
    
    if request.method == "POST":
        try:
            # Só atualiza se o campo vier no POST e não estiver vazio
            # (Mantém o valor antigo se o utilizador enviou vazio por erro)
            
            nome = request.POST.get('nome')
            if nome: dador.nome = nome

            nif = request.POST.get('nif')
            if nif: dador.nif = nif
            
            dador.contacto = request.POST.get('contacto')
            
            data = request.POST.get('dataNascimento')
            if data: dador.dataNascimento = data
            
            tipoSangue = request.POST.get('tipoSangue')
            if tipoSangue: dador.tipoSangue = tipoSangue
            
            sexo = request.POST.get('sexo')
            if sexo: dador.sexo = sexo
            
            novo_peso = request.POST.get('peso')
            if novo_peso:
                # Troca vírgula por ponto para evitar erros de float
                dador.peso = float(novo_peso.replace(',', '.'))
            
            # Checkboxes: se não estiver no POST, é False. Se estiver, é True.
            #dador.ativo = 'ativo' in request.POST
            dador.medicacao = 'medicacao' in request.POST
            dador.tatuagem = 'tatuagem' in request.POST
            dador.piercing = 'piercing' in request.POST
            dador.doente = 'doente' in request.POST
            
            dador.save()
            messages.success(request, f"Dados de {dador.nome} atualizados com sucesso!")
            
            if tipo_user == 'ADMIN':
                return redirect('menu_outros')
            else:
                return redirect('posto_selecionar_para_atualizar') # Volta para a lista
                
        except Exception as e:
            messages.error(request, f"Erro ao atualizar: {e}")

    return render(request, 'atualizar_dador.html', {'dador': dador, 'tipo_user': tipo_user})

# ///////////////////////// Posto \\\\\\\\\\\\\\\\\\\\\\\

@login_required
@user_passes_test(lambda u: u.utilizador.tipo == 'POSTO')
def home_posto(request):
    return render(request, 'posto.html')


# ///////////////////////// Hospital \\\\\\\\\\\\\\\\\\\\\\\

@login_required
@user_passes_test(lambda u: u.utilizador.tipo == 'HOSPITAL')
def home_hospital(request):
    return render(request, 'hospital_home.html')



def logout_view(request):
    logout(request)
    messages.success(request, "Sessão terminada.")
    return redirect('login') # Manda de volta para a tela de login