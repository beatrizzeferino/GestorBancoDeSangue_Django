from rest_framework import viewsets
from .permissions import IsAdmin, IsAdminOrPosto, IsAdminOrHospital
from ..models import Posto, Hospital, Dador, Doacao, StockSangue, PedidoHospital
from .serializers import (
    DadorSerializer, DoacaoSerializer, 
    StockSerializer, PedidoHospitalarSerializer,
    PostoSerializer, HospitalSerializer
)
class PostoViewSet(viewsets.ReadOnlyModelViewSet): #são só readOnly pois postos e hospitais estão associados a utilizadores e envolvem criar contas de aceso 
    queryset = Posto.objects.all()
    serializer_class = PostoSerializer
    permission_classes = [IsAdmin] # Apenas Admin gere a lista de postos

class HospitalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    permission_classes = [IsAdmin]

class DadorViewSet(viewsets.ModelViewSet):
    queryset = Dador.objects.all()
    serializer_class = DadorSerializer
    permission_classes = [IsAdminOrPosto]

class DoacaoViewSet(viewsets.ModelViewSet):
    queryset = Doacao.objects.all()
    serializer_class = DoacaoSerializer
    permission_classes = [IsAdminOrPosto]

class StockViewSet(viewsets.ModelViewSet):
    queryset = StockSangue.objects.all()
    serializer_class = StockSerializer
    permission_classes = [IsAdmin]

class PedidoHospitalarViewSet(viewsets.ModelViewSet):
    queryset = PedidoHospital.objects.all()
    serializer_class = PedidoHospitalarSerializer
    permission_classes = [IsAdmin]
