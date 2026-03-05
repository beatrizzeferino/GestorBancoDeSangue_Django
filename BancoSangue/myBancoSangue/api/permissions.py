from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view): 
        return (request.user.is_authenticated and #verifica se fez o login
                hasattr(request.user, 'utilizador') and #verifica se tem um perfil utilizador
                request.user.utilizador.tipo == 'ADMIN') #verifica se é admin



class IsAdminOrPosto(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                hasattr(request.user, 'utilizador') and 
                request.user.utilizador.tipo in ['ADMIN', 'POSTO'])

class IsAdminOrHospital(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                hasattr(request.user, 'utilizador') and 
                request.user.utilizador.tipo in ['ADMIN', 'HOSPITAL'])