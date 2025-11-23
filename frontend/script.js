const API_URL = "http://localhost:8000";

// --- NAVEGAÇÃO SPA (Single Page Application) ---
function navigateTo(viewId) {
    // 1. Esconder todas as views
    document.querySelectorAll('section[id^="view-"]').forEach(el => el.classList.add('hidden'));
    
    // 2. Remover classe active de todos os botões
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    
    // 3. Mostrar view desejada e ativar botão
    document.getElementById(`view-${viewId}`).classList.remove('hidden');
    document.getElementById(`nav-${viewId}`).classList.add('active');

    // 4. Atualizar Título da Página
    const titles = {
        'dashboard': 'Painel de Controle',
        'motoristas': 'Gestão de Frota',
        'relatorios': 'Relatórios Financeiros'
    };
    document.getElementById('page-title').innerText = titles[viewId];
}

// --- CORE LOGIC ---

async function carregarCorridas() {
    try {
        const res = await fetch(`${API_URL}/corridas`);
        if (!res.ok) throw new Error("API Offline");
        const dados = await res.json();
        
        // Atualiza Dashboard
        atualizarDashboard(dados);
        
        // Atualiza Tela Motoristas (Processamento no Front)
        renderizarTabelaMotoristas(dados);
        
        // Atualiza Relatórios
        atualizarRelatorios(dados);

        renderizarTabela(dados);
    } catch (e) {
        console.warn("API Offline", e);
    }
}

function atualizarDashboard(dados) {
    // KPI: Total Corridas
    document.getElementById('totalCorridasBadge').innerText = dados.length;
    
    // KPI: Valor Total
    const total = dados.reduce((acc, curr) => acc + (curr.valor_corrida || 0), 0);
    document.getElementById('totalValor').innerText = formatCurrency(total);
}

function atualizarRelatorios(dados) {
    const total = dados.reduce((acc, curr) => acc + (curr.valor_corrida || 0), 0);
    const media = dados.length > 0 ? total / dados.length : 0;
    
    document.getElementById('ticketMedio').innerText = formatCurrency(media);
}

// Algoritmo para agrupar dados por Motorista (Senior Logic)
function renderizarTabelaMotoristas(dados) {
    const motoristasMap = {};

    dados.forEach(c => {
        const nome = c.motorista.nome;
        if (!motoristasMap[nome]) {
            motoristasMap[nome] = { nome: nome, corridas: 0, total: 0 };
        }
        motoristasMap[nome].corridas += 1;
        motoristasMap[nome].total += (c.valor_corrida || 0);
    });

    const tbody = document.getElementById('tabelaMotoristas');
    tbody.innerHTML = '';

    Object.values(motoristasMap).forEach(m => {
        const row = `
            <tr class="hover:bg-slate-50 transition bg-white">
                <td class="px-6 py-4 font-semibold text-slate-700">${m.nome}</td>
                <td class="px-6 py-4">
                    <span class="badge badge-processada">Ativo</span>
                </td>
                <td class="px-6 py-4 text-center text-slate-600">${m.corridas}</td>
                <td class="px-6 py-4 text-right font-mono font-bold text-indigo-600">${formatCurrency(m.total)}</td>
                <td class="px-6 py-4 text-center">
                    <div class="flex justify-center text-yellow-400 text-sm">
                        <i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i><i class="ph-fill ph-star"></i>
                    </div>
                </td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

function renderizarTabela(dados) {
    const tbody = document.getElementById('tabelaCorridas');
    tbody.innerHTML = ''; 

    dados.reverse().forEach(c => {
        const isProc = c.status === 'processada';
        const badgeClass = isProc ? 'badge-processada' : 'badge-pendente';
        const icon = isProc ? 'ph-check-circle' : 'ph-hourglass';
        const rowClass = isProc ? 'bg-white' : 'bg-slate-50/50';

        const row = `
            <tr class="table-row-anim hover:bg-slate-50 transition ${rowClass}">
                <td class="px-6 py-4">
                    <span class="badge ${badgeClass}"><i class="ph-bold ${icon}"></i> ${c.status}</span>
                </td>
                <td class="px-6 py-4 font-medium text-slate-700">${c.motorista.nome}</td>
                <td class="px-6 py-4 text-xs text-slate-500">${c.origem} <i class="ph-bold ph-arrow-right mx-1"></i> ${c.destino}</td>
                <td class="px-6 py-4 text-right font-mono font-bold text-slate-800">${formatCurrency(c.valor_corrida)}</td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

async function checkSaldo() {
    const motorista = document.getElementById('motoristaSaldo').value;
    try {
        const res = await fetch(`${API_URL}/saldo/${motorista}`);
        if (!res.ok) return;
        const data = await res.json();
        const el = document.getElementById('saldoValor');
        const novoValor = formatCurrency(data.saldo);
        
        if (el.innerText !== novoValor && el.innerText !== "R$ 0,00") {
            el.classList.add("text-emerald-300", "scale-105");
            setTimeout(() => el.classList.remove("text-emerald-300", "scale-105"), 300);
            showToast(`Saldo atualizado: ${novoValor}`, 'success');
        }
        el.innerText = novoValor;
    } catch (e) {}
}

// --- FUNCIONALIDADE DE EXPORTAÇÃO (CSV) ---
async function exportarCSV() {
    const btn = document.getElementById('btnExport');
    const originalContent = btn.innerHTML;
    
    try {
        btn.innerHTML = `<i class="ph-bold ph-spinner animate-spin"></i> Gerando...`;
        btn.disabled = true;

        // 1. Busca os dados mais recentes
        const res = await fetch(`${API_URL}/corridas`);
        if (!res.ok) throw new Error("Erro ao buscar dados");
        const dados = await res.json();

        if (dados.length === 0) {
            showToast("Não há dados para exportar", "error");
            return;
        }

        // 2. Cria o cabeçalho do CSV
        let csvContent = "ID,Data,Passageiro,Motorista,Origem,Destino,Valor,Forma Pagamento,Status\n";

        // 3. Preenche as linhas
        dados.forEach(row => {
            // Tratamento para evitar quebras se tiver vírgula no texto
            const origem = `"${row.origem.replace(/"/g, '""')}"`; 
            const destino = `"${row.destino.replace(/"/g, '""')}"`;
            const valor = row.valor_corrida.toFixed(2).replace('.', ','); // Formato PT-BR
            const dataHoje = new Date().toLocaleDateString('pt-BR');

            csvContent += `${row._id},${dataHoje},${row.passageiro.nome},${row.motorista.nome},${origem},${destino},"${valor}",${row.forma_pagamento},${row.status}\n`;
        });

        // 4. Cria o arquivo Blob para download
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        
        // 5. Cria um link invisível e clica nele
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `relatorio_transflow_${Date.now()}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        showToast("Relatório exportado com sucesso!", "success");

    } catch (error) {
        console.error(error);
        showToast("Erro ao exportar dados", "error");
    } finally {
        btn.innerHTML = originalContent;
        btn.disabled = false;
    }
}

// --- UTILS ---
function formatCurrency(val) {
    return val.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    const styles = type === 'success' ? 'bg-white border-l-4 border-emerald-500 text-slate-800' : 'bg-white border-l-4 border-rose-500 text-slate-800';
    const icon = type === 'success' ? 'ph-check-circle text-emerald-500' : 'ph-warning-circle text-rose-500';

    toast.className = `toast flex items-center gap-3 px-6 py-4 rounded-lg shadow-xl border border-slate-100 min-w-[320px] ${styles}`;
    toast.innerHTML = `<i class="ph-fill ${icon} text-2xl"></i><div><p class="text-xs text-slate-500">${message}</p></div>`;
    container.appendChild(toast);
    setTimeout(() => { toast.remove(); }, 4000);
}

// --- INIT ---
document.getElementById('formCorrida').addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = e.target.querySelector('button');
    const original = btn.innerHTML;
    btn.innerHTML = `<i class="ph-bold ph-spinner animate-spin"></i> Processando...`;
    btn.disabled = true;

    const payload = {
        passageiro: { nome: document.getElementById('passNome').value, telefone: "000" },
        motorista: { nome: document.getElementById('motoristaSelect').value, nota: 5.0 },
        origem: document.getElementById('origem').value,
        destino: document.getElementById('destino').value,
        valor_corrida: parseFloat(document.getElementById('valor').value),
        forma_pagamento: "Pix"
    };

    try {
        await fetch(`${API_URL}/corridas`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)});
        showToast("Corrida Criada!", "success");
        carregarCorridas();
        document.getElementById('passNome').value = "";
    } catch (error) { showToast("Erro API", "error"); } 
    finally { btn.innerHTML = original; btn.disabled = false; }
});

document.getElementById('motoristaSaldo').addEventListener('change', checkSaldo);
setInterval(() => { carregarCorridas(); checkSaldo(); }, 2000);
carregarCorridas();
checkSaldo();