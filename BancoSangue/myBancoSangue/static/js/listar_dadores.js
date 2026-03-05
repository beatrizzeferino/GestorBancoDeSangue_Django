/* =========================================================
   1. ALTERNAR ABAS (TABS)
   ========================================================= */
function openTab(tabId, btnElement) {
    // Esconder todos os conteúdos
    const contents = document.querySelectorAll('.tab-content');
    contents.forEach(function(div) {
        div.style.display = 'none';
        div.classList.remove('active-content');
    });

    // Desativar todos os botões
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(function(btn) {
        btn.classList.remove('active');
    });

    // Ativar o conteúdo certo
    const activeContent = document.getElementById(tabId);
    if (activeContent) {
        activeContent.style.display = 'block';
        activeContent.classList.add('active-content');
    }

    // Ativar o botão certo
    if (btnElement) {
        btnElement.classList.add('active');
    }
}

/* =========================================================
   2. ORDENAR TABELA (Blindado para funcionar com <b> e NIFs)
   ========================================================= */
function ordenarTabela(n, tabelaId) {
    var table = document.getElementById(tabelaId);
    
    // Segurança: Se não encontrar a tabela, para a função
    if (!table) {
        console.error("Erro: Tabela " + tabelaId + " não encontrada.");
        return;
    }

    var rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
    switching = true;
    dir = "asc"; // Começa ascendente (A-Z ou 0-9)

    while (switching) {
        switching = false;
        rows = table.rows;

        // Loop pelas linhas (começa em 1 para saltar o cabeçalho)
        for (i = 1; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            
            // Pega nas células (TD) da coluna clicada (n)
            x = rows[i].getElementsByTagName("TD")[n];
            y = rows[i + 1].getElementsByTagName("TD")[n];

            if (!x || !y) continue;

            // .textContent limpa o HTML (remove os <b></b>) e fica só com o texto
            var xVal = x.textContent.trim().toLowerCase();
            var yVal = y.textContent.trim().toLowerCase();

            // Tenta detetar se é número (remove espaços vazios para NIFs)
            // Ex: "248 567" vira "248567" para ordenar corretamente
            var xNum = parseFloat(xVal.replace(/\s/g, ''));
            var yNum = parseFloat(yVal.replace(/\s/g, ''));
            
            // Verifica se ambas as células contêm números válidos
            var isNumeric = !isNaN(xNum) && !isNaN(yNum) && xVal !== "" && yVal !== "";

            if (dir == "asc") {
                if (isNumeric) {
                    if (xNum > yNum) shouldSwitch = true;
                } else {
                    // Ordenação de texto normal (localeCompare lida bem com acentos)
                    if (xVal.localeCompare(yVal) > 0) shouldSwitch = true;
                }
            } else if (dir == "desc") {
                if (isNumeric) {
                    if (xNum < yNum) shouldSwitch = true;
                } else {
                    if (xVal.localeCompare(yVal) < 0) shouldSwitch = true;
                }
            }
            
            if (shouldSwitch) {
                // Troca as linhas de lugar
                rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                switching = true;
                switchcount++;
                break; 
            }
        }
        
        // Se não houve trocas e a direção era "asc", muda para "desc" e corre de novo
        if (switchcount == 0 && dir == "asc") {
            dir = "desc";
            switching = true;
        }
    }
}

/* =========================================================
   3. FILTRAR POR SANGUE (Header)
   ========================================================= */
function filtrarSangueHeader(selectObject) {
    var filtro = selectObject.value;
    var table = selectObject.closest("table");
    var tr = table.getElementsByTagName("tr");

    for (var i = 1; i < tr.length; i++) {
        // Coluna do Sangue é a índice 2 (Nome=0, Nif=1, Sangue=2)
        var td = tr[i].getElementsByTagName("td")[2];
        
        // Ignora mensagens de tabela vazia
        if (tr[i].querySelector(".empty-message")) continue;

        if (td) {
            var txtValue = td.textContent || td.innerText;
            if (filtro === "todos" || txtValue.trim() === filtro) {
                tr[i].style.display = "";
            } else {
                tr[i].style.display = "none";
            }
        }
    }
}