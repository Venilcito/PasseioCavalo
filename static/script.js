const ws = new WebSocket("ws://localhost:8000/cavalo");

// referências aos elementos visuais (tabuleiro e botões)
const canvas = document.getElementById('tabuleiro');
const ctx = canvas.getContext('2d');
const botaoD = document.getElementById('btn-dfs');
const botaoA = document.getElementById('btn-a');
const botaoReset = document.getElementById('btn-reset');
const inputTempo = document.getElementById('input-tempo');

// Referências aos elementos da interface onde serão exibidas as métricas
const listaCaminho = document.getElementById("lista-caminho");
const algoritmoInfo = document.getElementById("algoritmo");
const geradosInfo = document.getElementById("gerados");
const expandidosInfo = document.getElementById("expandidos");
const tempoInfo = document.getElementById("tempo");

const tamanhoCasa = canvas.width/8;
let cavaloX = null;
let cavaloY = null;

let caminho = [];
let opcoes = false; // mostrar opções de movimento (quando clica no cavalo)

// quando RECEBER uma resposta do python
ws.onmessage = function(event){
    const data = JSON.parse(event.data);
    console.log("Recebido:", data);

    if(data.status === "rodando"){
        // Atualiza as métricas
        algoritmoInfo.textContent = data.algoritmo.toUpperCase();
        geradosInfo.textContent = data.ger;
        expandidosInfo.textContent = data.exp;
        tempoInfo.textContent = data.tempo.toFixed(5) + " s";

        // Atualiza o caminho
        caminho = data.caminho;

        const atual = caminho[caminho.length - 1];
        cavaloX = atual.x;
        cavaloY = atual.y;

        renderizar();
    }

    if(data.status === "fim"){
        botaoReset.disabled = false;
    }

    exibirCaminhoFinal();
};

// quando o usuário CLICA em algum lugar do tabuleiro
canvas.addEventListener('click', function(event){
    const rect = canvas.getBoundingClientRect();
    const clickX = Math.floor((event.clientX - rect.left) / tamanhoCasa);
    const clickY = Math.floor((event.clientY - rect.top) / tamanhoCasa);

    if (caminho.length === 0) {
        // se ainda não tiver nenhum caminho criado, coloca o cavalo na casa clicada
        caminho.push({x: clickX, y: clickY});
        cavaloX = clickX;
        cavaloY = clickY;
        
        botaoD.disabled = false;
        botaoA.disabled = false;
    } else{
        // se clicar no cavalo, exibe opções válidas de movimento
        const atual = caminho[caminho.length - 1];

        if (clickX === atual.x && clickY === atual.y) {
            opcoes = !opcoes; 
        } else{
            const validos = moveValido(atual.x, atual.y);
            const cliqueValido = validos.some(m => m.x === clickX && m.y === clickY);

            // se clicar em uma das opções válidas, adiciona a casa no caminho
            if (cliqueValido && opcoes) {
                caminho.push({x: clickX, y: clickY});
                cavaloX = clickX; 
                cavaloY = clickY;
                
                opcoes = false; 
            } else {
                opcoes = false;
            }
        }
    }

    renderizar();
});

// BOTÕES!!
botaoD.addEventListener('click', () => iniciarAlgoritmo("dfs"));
botaoA.addEventListener('click', () => iniciarAlgoritmo("ida*"));
botaoReset.addEventListener('click', () => window.location.reload());

// função para gerar as casas possíveis para movimentar o cavalo
function moveValido(x, y){
    const possiveis = [
        {x: x+1, y: y-2}, {x: x+2, y: y-1}, {x: x+2, y: y+1}, {x: x+1, y: y+2},
        {x: x-1, y: y+2}, {x: x-2, y: y+1}, {x: x-2, y: y-1}, {x: x-1, y: y-2}
    ];

    return possiveis.filter(m => {
        if (m.x < 0 || m.x > 7 || m.y < 0 || m.y > 7) return false;
        
        const jaVisitou = caminho.some(casa => casa.x === m.x && casa.y === m.y);
        if (jaVisitou) return false;

        return true;
    });
}

// MANDA o algoritmo e o caminho inicial para o python
function iniciarAlgoritmo(escolha) {
    if (caminho.length === 0) return;

    let tempo = parseFloat(inputTempo.value);
    if(isNaN(tempo) || tempo <= 0){ tempo = 100.0; }

    const config = {
        algoritmo: escolha,
        inicio: caminho,
        max: tempo
    };

    ws.send(JSON.stringify(config));
    console.log(`Enviando para rodar ${escolha}`);

    // desabilita os botões para prevenção de engraçadinhos
    botaoD.disabled = true;
    botaoA.disabled = true;
}

// funções de renderização que mexem no canvas do HTML
function desenharTabuleiro(){
    for(let coluna = 0; coluna < 8; coluna++){
        for(let linha = 0; linha < 8; linha++){
            if((coluna+linha)%2 === 0){
                ctx.fillStyle = '#EEEED2';
            } else{
                ctx.fillStyle = '#769656';
            }

            ctx.fillRect(coluna*tamanhoCasa, linha*tamanhoCasa, tamanhoCasa, tamanhoCasa);
        }
    }
}

function desenharCavalo() {
    if(caminho.length === 0) return;

    ctx.font = "35px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillStyle = '#000000';
    
    const pixelX = (cavaloX * tamanhoCasa) + (tamanhoCasa / 2);
    const pixelY = (cavaloY * tamanhoCasa) + (tamanhoCasa / 2);
    
    ctx.fillText("♞", pixelX, pixelY);
}

function desenharCaminho() {
    ctx.fillStyle = 'rgba(255, 0, 0, 0.3)';

    for(let i = 0; i < caminho.length; i++){
        const casa = caminho[i];
        ctx.fillRect(casa.x * tamanhoCasa, casa.y * tamanhoCasa, tamanhoCasa, tamanhoCasa);
    }

    //if(caminho.length < 2) return;

    ctx.strokeStyle = '#ff0000';
    ctx.lineWidth = 3;
    ctx.beginPath();

    for(let i = 0; i < caminho.length; i++){
        const casa = caminho[i];

        const centroX = (casa.x * tamanhoCasa) + (tamanhoCasa / 2);
        const centroY = (casa.y * tamanhoCasa) + (tamanhoCasa / 2);

        if (i === 0) {
            ctx.moveTo(centroX, centroY);
        } else {
            ctx.lineTo(centroX, centroY);
        }
    }

    ctx.stroke();
}

function desenharDestaques() {
    if (!opcoes || caminho.length === 0) return;

    const atual = caminho[caminho.length - 1];
    const validos = moveValido(atual.x, atual.y);
    
    ctx.fillStyle = 'rgba(0, 150, 255, 0.3)';
    
    for (let i = 0; i < validos.length; i++) {
        const m = validos[i];
        ctx.fillRect(m.x * tamanhoCasa, m.y * tamanhoCasa, tamanhoCasa, tamanhoCasa);
    }
}

// Função para marcar a casa inicial da lista na interface 
function sinalizarCasaInicial() {
    listaCaminho.innerHTML = "";
    if (caminho.length > 0) {
        const casa = caminho[0];
        const li = document.createElement("li");
        li.style.padding = "4px 0";
        li.style.color = "black";
        li.style.listStyleType = "none";
        li.style.marginLeft = "-20px";
        li.innerHTML = `<span style="color: #769656; font-weight: bold;">Casa Inicial:</span> (${casa.y}, ${casa.x})<br><span style="color: #888; font-size: 14px; font-style: italic;">Aguardando execução...</span>`;
        listaCaminho.appendChild(li);
    }
}

// Função que gera o caminho final para usar na interface 
function exibirCaminhoFinal() {
    listaCaminho.innerHTML = "";

    if (caminho.length === 0) {
        listaCaminho.innerHTML = '<li style="color: #666; font-style: italic; list-style-type: none; margin-left: -20px;">Nenhum caminho encontrado</li>';
        return;
    }

    caminho.forEach((casa, index) => {
        const li = document.createElement("li");
        li.style.padding = "4px 0";
        li.style.borderBottom = "1px solid #EEE";
        li.style.color = "black";
        
        if (index === 0) {
            li.innerHTML = `<span style="color: #769656; font-weight: bold;">Casa Inicial:</span> ( ${casa.y + 1}, ${casa.x + 1})`;
            li.style.listStyleType = "none";
            li.style.marginLeft = "-20px";
        } else {
            li.innerHTML = `<span style="font-weight: normal; color: #333;">Movimento ${index}:</span> <strong>(${casa.y + 1}, ${casa.x + 1})</strong>`;
        }
        
        listaCaminho.appendChild(li);
    });

    listaCaminho.scrollTop = 0; // Reseta a barra de rolagem para o topo
}

function renderizar() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    desenharTabuleiro();
    desenharCaminho();
    desenharDestaques();
    desenharCavalo();
}

renderizar();