from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Posto(models.Model):
    nome= models.CharField(max_length=100)
    nif= models.CharField(max_length=9, unique=True) #cada posto tem um nif único
    contacto= models.CharField(max_length=20)
    morada= models.CharField(max_length=200)

    def __str__(self):
        return f"Posto {self.nome}"
    
class Hospital(models.Model):
    nome= models.CharField(max_length=100)
    nif= models.CharField(max_length=9, unique=True)
    contacto= models.CharField(max_length=20)
    morada= models.CharField(max_length=200)

    def __str__(self):
        return self.nome

class Utilizador(models.Model):

    TIPOS_UTILIZADOR = [
        ('ADMIN', 'Administrador'),
        ('POSTO', 'Posto'),
        ('HOSPITAL', 'Hospital'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE) #utilizador de login for removido, o seu perfil no banco de sangue também é apagado
    tipo = models.CharField(max_length=10, choices=TIPOS_UTILIZADOR)

    posto = models.OneToOneField(Posto, on_delete=models.CASCADE, null=True, blank=True) #utilizador pode estar associado a um posto específico caso for um ou não caso não seja
    hospital = models.OneToOneField(Hospital, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.tipo})"

class Dador(models.Model):

    TIPO_SANGUE = [
        ('A+', 'A+'), #primeiro elem é o que fica na database o segunto é o que aparece nos formulários
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    SEXO = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    ]

    nome= models.CharField(max_length=100)
    nif= models.CharField(max_length=9, unique=True) #unique garante que nao ha dois registos de nif iguais
    contacto= models.CharField(max_length=20)
    dataNascimento= models.DateField()  
    tipoSangue= models.CharField(max_length=3, choices=TIPO_SANGUE)
    sexo= models.CharField(max_length=1, choices=SEXO)
    ativo= models.BooleanField(default=True)    #dador quando é registrado está imediatamente como ativo, só quando o admin ou posto pretende realmente desativar o dador é que ele pode ficar inativo

    #dados aptidao do dador
    peso = models.FloatField(validators=[MinValueValidator(0.0)]) #o peso é um float e impede que tenha valores negativos
    medicacao = models.BooleanField(default=False) #medicacao verdadeira significa que dador tomou medicacao recentemente
    tatuagem = models.BooleanField(default=False) #tatuagem verdadeira significa que dador fez uma tatuagem nos últimos 12 meses
    piercing = models.BooleanField(default=False) #piercing verdadeiro significa que fez um piercing nos últimos 6 meses
    doente = models.BooleanField(default=False) #doente verdadeiro significa que dador este doente recentemente

    @property #permite que idade seja usada com um atributo do dador
    def idade(self): 
        hoje= timezone.now().date()
        return (hoje -self.dataNascimento).days // 365
    
    @property #torna um metodo como uma propriedade, podemos acessa-lo como se fosse um atributo
    def aptidaoAtual(self): #verifica se um dador esta apto para fazer uma doação de sangue
        if self.peso <50: #so esta apto se tive mais de 50kg
            return False
        
        if not (18 <=self.idade <=65): #dador tem de ter entre 18 e 65 anos para poder doar
            return False
        
        if self.medicacao or self.tatuagem or self.piercing or self.doente: #nenhum destes parametros podem ser true, senao dador nao estara apto para doar sangue
            return False
        
        ultima_doacao= self.doacoes.order_by('-data').first() #ordem decrescente das datas das doacoes
        if ultima_doacao:
            meses=(timezone.now().date().year - ultima_doacao.data.year)*12 + (timezone.now().date().month - ultima_doacao.data.month) #calcula quanto tempo passou desde a ultima doacao
            
            if self.sexo == 'F':
                return meses >= 4 #mulheres tem de esperar 4 meses para poderem doar sangue novamente
            if self.sexo == 'M':
                return meses >= 3 #homens tem de esperar 3 meses para poderem doar sangue novamente
        return True
                
    def __str__(self):
        return self.nome
    


class Doacao(models.Model):
    dador=models.ForeignKey(Dador, on_delete=models.PROTECT, related_name='doacoes') #Se tentar apagar o dador associado a uma doacao, o Django dá um erro e obriga-o a decidir o que fazer com as doações primeiro; doacoes sao as doacoes associadas a um dador
    posto= models.ForeignKey(Posto, on_delete=models.PROTECT, related_name='doacoes') #Se tentar apagar o posto que ta associado a uma doacao, o Django dá um erro e obriga-o a decidir o que fazer com as doações primeiro; doacoes sao as doacoes associadas a um posto
    data= models.DateField(default=timezone.now)
    quantidade= models.FloatField(validators=[MinValueValidator(0.0)])
    @property
    def tipoSangue(self): #vai buscar o tipo de sangue da doacao ao tipo de sangue do dador
        return self.dador.tipoSangue

    def __str__(self):
        return f"Doação de {self.dador.nome} em {self.data}"
    
class StockSangue(models.Model):

    COMPONENTE=[
        ('GV', 'Glóbulos Vermelhos'),
        ('PL', 'Plasma'),
        ('PQ', 'Plaquetas'),
    ]

    tipoSangue=models.CharField(max_length=3, choices=Dador.TIPO_SANGUE)
    componente=models.CharField(max_length=2, choices=COMPONENTE)
    quantidade=models.FloatField(validators=[MinValueValidator(0.0)])
    limiteMinimo= models.FloatField(validators=[MinValueValidator(0.0)], default=200.0) #stock minimo dafault é 200 e é obrigatoriamente um valor positivo
    limiteMaximo = models.FloatField(validators=[MinValueValidator(0.0)], default=1000000000.0) #stock maximo dafault é 1000000000 e é obrigatoriamente um valor positivo

    class Meta:
        unique_together=('tipoSangue', 'componente') #garante que só há um stock por combinacao de componente tipo sanguineo

    def __str__(self):
        return f"Tipo sanguíneo {self.tipoSangue}, {self.get_componente_display()}: {self.quantidade}"
    

    
class PedidoHospital(models.Model):

    ESTADO_PEDIDO=[
        ('A', 'Aprovado'),
        ('R', 'Rejeitado'),
        ('P', 'Pendente'),
    ]

    hospital=models.ForeignKey(Hospital, on_delete=models.PROTECT, related_name='pedidos') # impede que hospitais que estão associados a pedidos sejam apagados; pedidos permite que o hospital guarde todos os pedidos associados a ele
    tipo_sangue= models.CharField(max_length=3, choices=Dador.TIPO_SANGUE)
    quantidade=models.FloatField(validators=[MinValueValidator(0.0)])
    componente=models.CharField(max_length=2, choices=StockSangue.COMPONENTE)
    estadoPedido=models.CharField(max_length=1, choices=ESTADO_PEDIDO)
    dataPedido= models.DateField(default=timezone.now)

    def __str__(self):
        return f"Pedido {self.id} do hospital {self.hospital.nome}: {self.estadoPedido}"

