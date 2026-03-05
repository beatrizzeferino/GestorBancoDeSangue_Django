from rest_framework import serializers
from ..models import Posto, Hospital, Dador, Doacao, StockSangue, PedidoHospital

class PostoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Posto
        fields = '__all__' #traduz todas as colunas do model para JSON

class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = '__all__'
        
class DadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dador
        fields = '__all__'

class DoacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doacao
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockSangue
        fields = '__all__'

class PedidoHospitalarSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoHospital
        fields = '__all__'