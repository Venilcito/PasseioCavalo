const ws = new WebSocket("ws://localhost:8000/ws/cavalo");

const canvas = document.getElementById('tabuleiro');
const ctx = canvas.getContext('2d');
const botaoD = document.getElementById('btn-dfs');
const botaoA = document.getElementById('btn-a');

const tamanhoCasa = canvas.width/8;
let cavaloX = null;
let cavaloY = null;
let caminho = [];

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

canvas.addEventListener('click', function(event) {
    const rect = canvas.getBoundingClientRect();
    const mouseX = event.clientX - rect.left;
    const mouseY = event.clientY - rect.top;

    const casaClicadaX = Math.floor(mouseX / tamanhoCasa);
    const casaClicadaY = Math.floor(mouseY / tamanhoCasa);

    cavaloX = casaClicadaX;
    cavaloY = casaClicadaY;
    renderizar();

    botaoD.disabled = false;
    botaoA.disabled = false;
    console.log(`Cavalo colocado em (${cavaloX}, ${cavaloY})`);
});

botaoD.addEventListener('click', () => iniciarAlgoritmo("dfs"));
botaoA.addEventListener('click', () => iniciarAlgoritmo("a*"));

function iniciarAlgoritmo(escolha) {
    if (cavaloX === null || cavaloY === null) return;

    const config = {
        algoritmo: escolha,
        inicio: { x: cavaloX, y: cavaloY }
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
    if (cavaloX !== null && cavaloY !== null) {
        ctx.font = "35px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillStyle = '#000000';
        
        const pixelX = (cavaloX * tamanhoCasa) + (tamanhoCasa / 2);
        const pixelY = (cavaloY * tamanhoCasa) + (tamanhoCasa / 2);
        
        ctx.fillText("♞", pixelX, pixelY);
    }
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

function renderizar() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    desenharTabuleiro();
    desenharCaminho();
    desenharCavalo();
}

renderizar();