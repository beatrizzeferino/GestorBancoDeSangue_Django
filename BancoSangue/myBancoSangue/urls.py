from django.urls import path
from . import views

urlpatterns=[
    #path('endereço_no_site', função_na_view, nome_do_atalho)
    #autenticacao e paginas iniciais
    path('', views.login_view, name='login'),
    path('home/admin/', views.home_admin, name='home_admin'),
    path('home/posto/', views.home_posto, name='home_posto'),
    path('home/hospital/', views.home_hospital, name='home_hospital'),
    path('logout/', views.logout_view, name='logout'),
    
    #admins
    path('home/admin/add_admin/', views.menu_add_admin, name='menu_add_admin'),

    path('home/admin/postos/', views.menu_postos, name='menu_postos'),
    path('home/admin/postos/criar/', views.criar_posto, name='criar_posto'),
    path('home/admin/postos/listar/', views.listar_postos, name='listar_postos'),
    path('home/admin/postos/procurar/', views.procurar_posto, name='procurar_posto'),
    path('home/admin/postos/selecionar-atualizar/', views.selecionar_posto_para_atualizar, name='selecionar_posto_para_atualizar'),
    path('home/admin/postos/atualizar/<int:posto_id>/', views.atualizar_posto, name='atualizar_posto'),

    path('home/admin/hospitais/', views.menu_hospitais, name='menu_hospitais'),
    path('home/admin/hospitais/criar/', views.criar_hospital, name='criar_hospital'),
    path('home/admin/hospitais/listar/', views.listar_hospitais, name='listar_hospitais'),
    path('home/admin/hospitais/procurar/', views.procurar_hospital, name='procurar_hospital'),
    path('home/admin/hospitais/selecionar-atualizar/', views.selecionar_hospital_para_atualizar, name='selecionar_hospital_para_atualizar'),
    path('home/admin/hospitais/atualizar/<int:hospital_id>/', views.atualizar_hospital, name='atualizar_hospital'),

    path('home/admin/doacoes/consultar/', views.consultar_doacoes, name='consultar_doacoes'),

    path('home/admin/pedidos/consultar/', views.consultar_pedidos_hospital, name='consultar_pedidos'),

    
    path('home/admin/relatorios/', views.gerar_relatorios, name='gerar_relatorios'),

    path('home/admin/stock/', views.menu_stock, name='menu_stock'),

    path('home/admin/outros/', views.menu_outros, name='menu_outros'),
    path('home/admin/outros/dadores/adicionar/', views.adicionar_dador, name='adicionar_dador'),
    path('home/admin/outros/doacoes/adicionar/', views.adicionar_doacao, name='adicionar_doacao'),
    path('home/admin/outros/pedidos/fazer/', views.fazer_pedido, name='fazer_pedido'),
    path('home/admin/outros/dadores/listar/', views.listar_dadores, name='listar_dadores'),
    path('home/admin/outros/dadores/procurar/', views.procurar_dador, name='procurar_dador'),
    path('home/admin/outros/dadores/selecionar-atualizar/', views.selecionar_dador_para_atualizar, name='selecionar_dador_para_atualizar'),
    path('home/admin/outros/dadores/ativar-desativar/', views.ativar_desativar_dador, name='ativar_desativar_dador'),
    path('home/admin/outros/dadores/atualizar/<int:dador_id>/', views.atualizar_dador, name='atualizar_dador'),
    
    #postos
    path('home/posto/dadores/adicionar/', views.adicionar_dador, name='posto_adicionar_dador'),
    path('home/posto/dadores/procurar/', views.procurar_dador, name='posto_procurar_dador'),
    path('home/posto/dadores/listar/', views.listar_dadores, name='posto_listar_dadores'),
    path('home/posto/dadores/ativar-desativar/', views.ativar_desativar_dador, name='posto_ativar_desativar'),
    path('home/posto/dadores/selecionar-atualizar/', views.selecionar_dador_para_atualizar, name='posto_selecionar_para_atualizar'),
    path('home/posto/dadores/atualizar/<int:dador_id>/', views.atualizar_dador, name='posto_atualizar_dador'),
    path('home/posto/doacoes/adicionar/', views.adicionar_doacao, name='posto_adicionar_doacao'),
    path('home/posto/doacoes/consultar/', views.consultar_doacoes, name='posto_consultar_doacoes'),
    
    #hospitais
    path('home/hospital/pedidos/fazer/', views.fazer_pedido, name='hospital_fazer_pedido'),
    path('home/hospital/stock/', views.menu_stock, name='hospital_menu_stock'),
    path('home/hospital/pedidos/consultar/', views.consultar_pedidos_hospital, name='hospital_consultar_pedidos'),
    ]
