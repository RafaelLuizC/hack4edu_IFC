// Carrega trilha e popula index ou activity
async function loadTrilha(){
  const res = await fetch('/atividades');
  const data = await res.json(); // array de atividades
  return data; // cada item: {Codigo, Atividade, Topico, Subtopico, Conteudo, Detalhes}
}

// Helper para criar elementos HTML.
function el(tag, cls, txt){ const e = document.createElement(tag); if(cls) e.className = cls; if(txt) e.textContent = txt; return e; }

// Página Index
async function renderIndex(){ // Função para renderizar a página inicial com a lista de lições
  const container = document.getElementById('lessons'); 
  const trilha = await loadTrilha(); 
  const grid = el('div','lesson-grid');
  
  trilha.forEach(item=>{ // cria card para cada atividade
    const card = el('div','card');
    card.onclick = ()=> location.href = '/activity/' + item.Codigo; // navega para a atividade, e passa o código na URL.
    
    const meta = el('div','meta', `${item.Codigo} • ${item.Atividade}`); // exibe código e tipo de atividade
    const h = el('h3',null, item.Topico + ' — ' + item.Subtopico); // título e subtítulo
    const p = el('p',null, item.Conteudo); // descrição
    
    card.append(meta,h,p); // Monta o card com as informações.
    grid.append(card); // Adiciona o card ao grid.
  });
  container.append(grid); // Adiciona o grid ao container principal.
}

// Página Activity
// Pagina de atividades, ela irá carregar a atividade conforme o código na URL.
async function renderActivity(codigo){
  
  const container = document.getElementById('activity-container'); 
  const trilha = await loadTrilha();
  const item = trilha.find(x=>x.Codigo === codigo);
  if(!item){ container.append(el('p',null,'Atividade não encontrada.')); return }

  const title = el('h2',null, item.Topico + ' — ' + item.Subtopico);
  container.append(title);

  if(item.Atividade === 'Flashcard'){
    const card = el('div','flashcard');
    const faceFront = document.createElement('div'); faceFront.className='card-face front'; faceFront.innerHTML = `<strong>${item.Detalhes.Flashcard.Frente}</strong>`;
    const faceBack = document.createElement('div'); faceBack.className='card-face back-face'; faceBack.innerHTML = `<div>${item.Detalhes.Flashcard.Verso}</div>`;
    card.append(faceFront, faceBack);
    const btn = el('button','flip-btn','Girar');
    btn.onclick = ()=> card.classList.toggle('flipped');
    container.append(card, btn);
    return;
  }

  if(item.Atividade === 'Quiz'){
    const q = item.Detalhes.Quiz;
    container.append(el('p',null,q.Pergunta));
    const opts = el('div','quiz-opts');
    q.Alternativas.forEach((alt, idx)=>{
      const o = el('div','opt', alt.Texto);
      o.onclick = ()=>{
        // feedback
        Array.from(opts.children).forEach(ch=>ch.classList.remove('correct','wrong'));
        if(alt.Correta){ o.classList.add('correct'); container.append(el('div','feedback','Correto! ' + (alt.Explicacao||''))) }
        else{ o.classList.add('wrong'); container.append(el('div','feedback','Incorreto. ' + (alt.Explicacao||''))) }
      };
      opts.append(o);
    });
    container.append(opts);
    return;
  }

  if(item.Atividade === 'Audio'){
    const a = item.Detalhes.Audio;
    container.append(el('p',null,a.Titulo));
    const player = el('div','audio-player');
    const btn = el('button','play-btn','▶');
    btn.onclick = ()=> playDialogue(a.Dialogo);
    player.append(btn);
    container.append(player);
    return;
  }

  if(item.Atividade === 'CacaPalavras'){
    const c = item.Detalhes.CacaPalavras;
    container.append(el('p',null,'Tema: ' + c.Tema));
    container.append(el('p',null,'Encontre as palavras abaixo:'));
    const wordList = el('div',null); c.Palavras.forEach(w=>{ wordList.append(el('span',null,w + ' ')) });
    container.append(wordList);

    // Gera grade simples com palavras ocultas (horizontal/vertical) - algoritmo simples
    const size = 10;
    const grid = Array.from({length:size},()=>Array.from({length:size},()=>String.fromCharCode(65 + Math.floor(Math.random()*26))));
    // tenta inserir palavras horizontalmente
    c.Palavras.forEach((word, i)=>{
      word = word.toUpperCase();
      const row = i % size;
      let col = Math.floor(Math.random() * (size - word.length));
      for(let k=0;k<word.length;k++) grid[row][col+k] = word[k];
    });

    const gridEl = el('div','wordgrid');
    gridEl.style.gridTemplateColumns = `repeat(${size}, 36px)`;
    for(let r=0;r<size;r++){
      for(let cidx=0;cidx<size;cidx++){
        const cell = el('div','grid-cell', grid[r][cidx]);
        cell.dataset.r = r; cell.dataset.c = cidx;
        gridEl.append(cell);
      }
    }
    container.append(gridEl);

    // seleção por clique em sequência
    let selection = [];
    gridEl.addEventListener('click', (ev)=>{
      const cell = ev.target.closest('.grid-cell'); if(!cell) return;
      cell.classList.toggle('selected');
      const txt = cell.textContent;
      selection.push(txt);
      const word = selection.join('');
      // checa se corresponde alguma palavra
      const found = c.Palavras.map(w=>w.toUpperCase()).find(w=>w === word);
      if(found){ alert('Você encontrou: ' + found); selection = []; Array.from(gridEl.querySelectorAll('.selected')).forEach(el=>el.classList.remove('selected')) }
    });

    return;
  }

  container.append(el('p',null,'Tipo de atividade desconhecido.'));
}

// TTS para diálogo de áudio
function playDialogue(dialogo){
  const utter = (text, onend)=>{
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'pt-BR';
    u.onend = onend;
    speechSynthesis.speak(u);
  };
  // encadeia as falas
  let idx = 0;
  const next = ()=>{
    if(idx >= dialogo.length) return;
    const parte = dialogo[idx++];
    utter(parte.Personagem + ': ' + parte.Fala, next);
  };
  next();
}

// Inicialização simples: decide qual página estamos
(function(){
  if(document.getElementById('lessons')) renderIndex();
  const activityContainer = document.getElementById('activity-container');
  if(activityContainer){
    // janela activity.html
    const codigo = window.codigo || (function(){ const p = location.pathname.split('/'); return p[p.length-1]; })();
    renderActivity(codigo);
  }
})();