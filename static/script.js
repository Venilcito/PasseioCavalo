const ws = new WebSocket("ws://localhost:8000/ws/cavalo");

const canvas = document.getElementById('tabuleiro');
const ctx = canvas.getContext('2d');
const botaoD = document.getElementById('btn-dfs');
const botaoA = document.getElementById('btn-a');

const tamanhoCasa = canvas.width/8;
let cavaloX = null;
let cavaloY = null;

let caminho = [];
let opcoes = false;

ws.onmessage = function(event){
    // pegando os resultados do python
    const data = JSON.parse(event.data);
    console.log("Recebido:", data);

    if(data.status === 'rodando'){
        caminho = data.caminho;

        const atual = caminho[caminho.length-1];
        cavaloX = atual.x;
        cavaloY = atual.y;
        renderizar();
    }
};

canvas.addEventListener('click', function(event){
    const rect = canvas.getBoundingClientRect();
    const clickX = Math.floor((event.clientX - rect.left) / tamanhoCasa);
    const clickY = Math.floor((event.clientY - rect.top) / tamanhoCasa);

    if (caminho.length === 0) {
        caminho.push({x: clickX, y: clickY});
        cavaloX = clickX;
        cavaloY = clickY;
        
        botaoD.disabled = false;
        botaoA.disabled = false;
    } else{
        const atual = caminho[caminho.length - 1];

        if (clickX === atual.x && clickY === atual.y) {
            opcoes = !opcoes; 
        } else{
            const validos = moveValido(atual.x, atual.y);
            const cliqueValido = validos.some(m => m.x === clickX && m.y === clickY);

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

botaoD.addEventListener('click', () => iniciarAlgoritmo("dfs"));
botaoA.addEventListener('click', () => iniciarAlgoritmo("a*"));

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

function iniciarAlgoritmo(escolha) {
    if (caminho.length === 0) return;

    const config = {
        algoritmo: escolha,
        inicio: caminho 
    };

    ws.send(JSON.stringify(config));
    console.log(`Enviando para rodar ${escolha}`);

    botaoD.disabled = true;
    botaoA.disabled = true;
}

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

function renderizar() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    desenharTabuleiro();
    desenharCaminho();
    desenharDestaques();
    desenharCavalo();
}

renderizar();