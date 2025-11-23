const API_URL = "http://localhost:8000";

// --- FUNÇÕES AUXILIARES ---

async function carregarCorridas() {
    try {
        const res = await fetch(`${API_URL}/corridas`);
        if (!res.ok) throw new Error("Falha ao buscar");
        
        const dados = await res.json();
        renderizarTabela(dados);
    } catch (e) {
        console.error("Erro ao buscar corridas:", e);
    }
}

function renderizarTabela(dados) {
    const tbody = document.getElementById('tabelaCorridas');
    tbody.innerHTML = ''; 

    // Reverte para mostrar as mais recentes no topo
    dados.reverse().forEach(c => {
        const isProcessada = c.status === 'processada';
        const statusClass = isProcessada ? 'status-processada' : 'status-pendente';
        const icon = isProcessada ? '✅' : '⏳';
        
        const row = `
            <tr class="border-b border-slate-700 last:border-0 fade-in hover:bg-white/5 transition">
                <td class="py-3 pl-2">
                    <span class="px-2 py-1 rounded text-xs font-bold ${statusClass}">
                        ${icon} ${c.status.toUpperCase()}
                    </span>
                </td>
                <td class="py-3 font-medium text-slate-200">${c.motorista.nome}</td>
                <td class="py-3 text-slate-400">${c.passageiro.nome} → ${c.destino}</td>
                <td class="py-3 text-right font-mono text-indigo-300">R$ ${c.valor_corrida.toFixed(2)}</td>
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
        const saldoFormatado = data.saldo.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
        
        // Efeito visual simples se mudar o valor (opcional)
        const el = document.getElementById('saldoValor');
        if (el.innerText !== saldoFormatado && el.innerText !== "R$ 0,00") {
            el.style.color = "#fff"; // Pisca branco
            setTimeout(() => el.style.color = "#4ade80", 300); // Volta verde
        }
        el.innerText = saldoFormatado;
        
    } catch (e) {
        console.error("Erro saldo", e);
    }
}

// --- EVENT LISTENERS ---

document.getElementById('formCorrida').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // UI Feedback
    const btn = e.target.querySelector('button');
    const textoOriginal = btn.innerText;
    btn.innerText = "Enviando...";
    btn.disabled = true;

    const payload = {
        passageiro: {
            nome: document.getElementById('passNome').value,
            telefone: "99999-9999"
        },
        motorista: {
            nome: document.getElementById('motoristaSelect').value,
            nota: 5.0
        },
        origem: document.getElementById('origem').value,
        destino: document.getElementById('destino').value,
        valor_corrida: parseFloat(document.getElementById('valor').value),
        forma_pagamento: "Pix"
    };

    try {
        const res = await fetch(`${API_URL}/corridas`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (res.ok) {
            // Atualiza dados imediatamente
            carregarCorridas();
            checkSaldo();
        } else {
            alert("Erro ao criar corrida: " + res.statusText);
        }
    } catch (error) {
        alert("Erro de conexão com API");
    } finally {
        // Reset UI
        btn.innerText = textoOriginal;
        btn.disabled = false;
        // Limpar campos principais
        document.getElementById('passNome').value = "";
    }
});

document.getElementById('motoristaSaldo').addEventListener('change', checkSaldo);

// --- INICIALIZAÇÃO ---

// Polling: Atualiza dados a cada 2 segundos
setInterval(() => {
    carregarCorridas();
    checkSaldo();
}, 2000);

// Primeira carga
carregarCorridas();
checkSaldo();