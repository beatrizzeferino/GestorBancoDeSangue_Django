document.addEventListener("DOMContentLoaded", function() {
    
    // Verifica se existe o cartão de resultado
    const resultado = document.getElementById('resultadoDador');
    
    if (resultado) {
        // Faz scroll suave até ao resultado para o utilizador ver logo
        resultado.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // Opcional: Limpar mensagens de erro após 5 segundos
    const alertas = document.querySelectorAll('.alerta');
    if (alertas.length > 0) {
        setTimeout(() => {
            alertas.forEach(alerta => {
                alerta.style.opacity = '0';
                setTimeout(() => alerta.remove(), 500); // Remove do DOM após fade out
            });
        }, 5000);
    }
});