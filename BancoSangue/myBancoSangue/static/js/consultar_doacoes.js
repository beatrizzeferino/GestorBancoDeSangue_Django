/* --- Lógica da página de Consultar Doações --- */

document.addEventListener("DOMContentLoaded", function() {
    
    // Verifica se estamos na página correta procurando pelo ID da área de filtros
    const areaFiltros = document.getElementById('areaFiltros');
    
    if (areaFiltros) {
        // 1. O TRUQUE PARA A VIEW ANTIGA FUNCIONAR
        if (!window.location.search) {
            window.location.replace("?modo=tudo");
        }

        // Recuperar o estado do filtro (abrir se houver pesquisa)
        const urlParams = new URLSearchParams(window.location.search);
        const modoAtual = urlParams.get('modo');
        const iconSeta = document.getElementById('iconSeta');
        
        if (modoAtual && modoAtual !== 'tudo') {
            areaFiltros.style.display = 'grid';
            if(iconSeta) iconSeta.className = 'fas fa-chevron-up';
        }
    }
});

// Esta função pode ficar fora, pois só é chamada quando alguém clica no botão
function toggleFiltros() {
    const area = document.getElementById('areaFiltros');
    const icon = document.getElementById('iconSeta');
    
    // Proteção extra caso a função seja chamada numa página sem estes elementos
    if (!area || !icon) return; 

    if (area.style.display === 'none') {
        area.style.display = 'grid';
        icon.className = 'fas fa-chevron-up';
    } else {
        area.style.display = 'none';
        icon.className = 'fas fa-chevron-down';
    }
}