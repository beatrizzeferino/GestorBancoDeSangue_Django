// Função para abrir a tab correta
function openTab(tabId, btnElement) {
    // 1. Esconder todos os conteúdos com a classe .tab-content
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(function(div) {
        div.style.display = 'none';
    });

    // 2. Remover a classe 'active' de todos os botões .tab-btn
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(function(btn) {
        btn.classList.remove('active');
    });

    // 3. Mostrar o conteúdo desejado (pelo ID passado)
    const activeContent = document.getElementById(tabId);
    if (activeContent) {
        activeContent.style.display = 'block';
    }

    // 4. Adicionar a classe 'active' ao botão clicado
    if (btnElement) {
        btnElement.classList.add('active');
    }
}

// Garantir que a aba "Aprovados" abre por defeito se o JS demorar a carregar
document.addEventListener("DOMContentLoaded", function() {
    const activeBtn = document.querySelector('.tab-btn.active');
    if (!activeBtn) {
        const firstBtn = document.querySelector('.tab-btn');
        if (firstBtn) {
            firstBtn.click();
        }
    }
});