function aplicarFiltros() {
    const tipo = document.getElementById('filtroTipo').value;
    const componente = document.getElementById('filtroComponente').value;
    const estado = document.getElementById('filtroEstado').value;

    document.querySelectorAll('#tabelaStock tr').forEach(linha => {
        const matchTipo = !tipo || linha.dataset.tipo === tipo;
        const matchComp = !componente || linha.dataset.componente === componente;
        const matchEstado = !estado || linha.dataset.estado === estado;

        linha.style.display = (matchTipo && matchComp && matchEstado) ? '' : 'none';
    });
}

document.querySelectorAll('.filtros select').forEach(filtro => {
    filtro.addEventListener('change', aplicarFiltros);
});