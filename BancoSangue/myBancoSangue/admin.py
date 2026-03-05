from django.contrib import admin

from .models import Dador,Utilizador, Posto, Doacao, StockSangue, Hospital, PedidoHospital

admin.site.register(Dador)
admin.site.register(Posto)
admin.site.register(Doacao)
admin.site.register(StockSangue)
admin.site.register(Hospital)
admin.site.register(PedidoHospital)
admin.site.register(Utilizador)