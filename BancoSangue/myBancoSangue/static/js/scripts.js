document.addEventListener('DOMContentLoaded', function() {
    // Procura por elementos com a classe .alerta (do teu CSS)
    const alertas = document.querySelectorAll('.alerta');
    
    if (alertas.length > 0) {
        setTimeout(function() {
            alertas.forEach(function(alerta) {
                // Animação de saída
                alerta.style.transition = "opacity 0.5s ease, transform 0.5s ease";
                alerta.style.opacity = "0";
                alerta.style.transform = "translateY(-20px)"; 
                
                // Remove do HTML após a transição
                setTimeout(() => alerta.remove(), 500);
            });
        }, 4000); // 4 segundos visível
    }
});

