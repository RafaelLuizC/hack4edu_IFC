async function loadTrilha(){
  const res = await fetch('/atividades');
  const data = await res.json();
  return data;
}

function el(tag, cls, txt, data) {
  const e = document.createElement(tag);
  if(cls) e.className = cls; 
  if(txt) e.textContent = txt;
  return e;
}

// --- INDEX (agrupa por Matéria e cria botão Iniciar para cada trilha por matéria) ---
async function renderIndex(){
  const container = document.getElementById('lessons');
  const trilha = await loadTrilha();
  // agrupa por Materia (mantendo ordem de primeira aparição)
  const grupos = {};
  const ordem = [];

  trilha.forEach(item => {
    const m = item.Materia || 'Geral';
    if (!grupos[m]) {
      grupos[m]=[];
      ordem.push(m);
    }
    grupos[m].push(item);
  });

  ordem.forEach(materia=>{
    const box = el('section','subject-box');
    box.append(el('h2',null,materia));
    const sub = el('div','subject-list');
    let topics = [];

    grupos[materia].forEach(item => {

      // Lista de atividades da seção.
      // const row = el('div','mat-row');
      // const title = el('div','mat-meta', `${item.Codigo} • ${item.Atividade} • ${item.Topico} — ${item.Subtopico}`);
      // row.append(title);
      // sub.append(row);

      if (!topics.includes(item.Topico)) {
        topics.push(item.Topico);
      }
    });

    const section = el('p','subject-section__title','Seção 1');
    let topicText = 'Exercícios de ';

    for (let topicIndex in topics) {
      topicText = topicText + topics[topicIndex];
      
      if (topicIndex < (topics.length - 2)) {
        topicText = topicText + ', ';
      
      } else if (topicIndex < (topics.length - 1)) {
        topicText = topicText + ' e ';
      }
    }
    
    const topicElement = el('p','subject-section__topics',topicText);
    box.append(section);
    box.append(topicElement);
    
    const startBtn = el('button','start-btn btn','Iniciar trilha');
    startBtn.onclick = () => { 
      const first = grupos[materia][0];
      if(first) location.href = '/activity/' + first.Codigo;
    };
    box.append(sub, startBtn);
    container.append(box);
  });
}

// --- ACTIVITY (renderização única por atividade, gerencia sequência e Continue) ---
async function renderActivityPage(codigo){
  const container = document.getElementById('activity-container');
  if(!container) return;

  const trilha = await loadTrilha();
  // lista de atividades da mesma matéria em ordem de aparição no JSON
  const current = trilha.find(x=>x.Codigo === codigo);
  if(!current){ container.append(el('p',null,'Atividade não encontrada.')); return }
  const materia = current.Materia || 'Geral';
  const grupo = trilha.filter(x=> (x.Materia||'Geral') === materia);
  const index = grupo.findIndex(x=>x.Codigo === codigo);

  // estado de sequência: armazenado em sessionStorage por matéria
  const stateKey = 'trilha_state_' + materia;
  let state = JSON.parse(sessionStorage.getItem(stateKey) || '{}');
  if(!state.startTime){ state.startTime = Date.now(); state.errors = 0; state.completed = 0; state.total = grupo.length; sessionStorage.setItem(stateKey, JSON.stringify(state)); }

  // UI base
  container.innerHTML = '';
  const title = el('h2',null, `${current.Topico} — ${current.Subtopico}`);
  container.append(title);

  const activityBox = el('div','activity-box');
  container.append(activityBox);

  const continueBtn = el('button','continue-btn disabled btn','Continuar');
  continueBtn.disabled = true; continueBtn.style.opacity = '0.5';
  continueBtn.onclick = ()=>{
    // marcar concluído e navegar ou finalizar
    state.completed = (state.completed||0) + 1;
    sessionStorage.setItem(stateKey, JSON.stringify(state));
    if(index < grupo.length - 1){
      const next = grupo[index+1];
      location.href = '/activity/' + next.Codigo;
    } else {
      showSummary(stateKey);
    }
  };
  container.append(continueBtn);

  function enableContinue(){
    continueBtn.disabled = false; continueBtn.classList.remove('disabled'); continueBtn.style.opacity = '1';
  }

  function addError(){
    state.errors = (state.errors||0) + 1;
    sessionStorage.setItem(stateKey, JSON.stringify(state));
  }

  // Render específico por tipo
  if(current.Atividade === 'Flashcard'){
    const card = el('div','flashcard');
    const faceFront = document.createElement('div');
    faceFront.className='card-face front';
    faceFront.innerHTML = `<strong>${current.Detalhes.Flashcard.Frente}</strong>`;
    const faceBack = document.createElement('div');
    faceBack.className='card-face back-face';
    faceBack.innerHTML = `<div>${current.Detalhes.Flashcard.Verso}</div>`;
    card.append(faceFront, faceBack);
    const btn = el('button','flip-btn btn','Girar');

    btn.onclick = () => {
      card.classList.toggle('flipped');
      // se girou (mostrar verso), considera completado
      if(card.classList.contains('flipped')) enableContinue();
    };
    activityBox.append(card, btn);
    return;
  }

  if(current.Atividade === 'Quiz'){
    const q = current.Detalhes.Quiz;
    activityBox.append(el('p',null,q.Pergunta));
    const opts = el('div','quiz-opts');
    let selectedIdx = null;
    q.Alternativas.forEach((alt, idx)=>{
      const o = el('div','opt', alt.Texto);
      o.onclick = ()=>{
        // seleção visual
        Array.from(opts.children).forEach(ch=>ch.classList.remove('selected'));
        o.classList.add('selected');
        selectedIdx = idx;
        // mostrar botão verificar (se não existe)
        if(!document.getElementById('verificar-btn')){
          const vbtn = el('button','verificar-btn btn','Verificar');
          vbtn.id = 'verificar-btn';
          vbtn.onclick = ()=>{
            const altSel = q.Alternativas[selectedIdx];
            if(altSel.Correta){
              o.classList.add('correct');
              activityBox.append(el('div','feedback','Correto! ' + (altSel.Explicacao||'')));
            } else {
              o.classList.add('wrong');
              activityBox.append(el('div','feedback','Incorreto. ' + (altSel.Explicacao||'')));
              addError();
            }
            // habilita continuar
            enableContinue();
            // desabilita verificação futura
            vbtn.disabled = true; vbtn.style.opacity = '0.6';
          };
          activityBox.append(vbtn);
        }
      };
      opts.append(o);
    });
    activityBox.append(opts);
    return;
  }

  if(current.Atividade === 'Audio'){
    const a = current.Detalhes.Audio;
    activityBox.append(el('p', null, a.Titulo));
    const player = el('div','audio-player');
    const btn = el('button','play-btn btn','▶ Ouvir');
    player.append(btn);
    activityBox.append(player);

    const id = codigo || current.Codigo;
    const audioPathBase = `/static/audios/`; // Caminho base dos áudios AGORA dentro de static
    const tryPath = (ext) => `${audioPathBase}${id}.${ext}`; // Recebe o caminho do audio com base no codigo da atividade.
    const candidate = tryPath('wav'); // Adiciona a extensão .wav como primeira tentativa.

    let fileExists = false;   // Verifica se o arquivo existe.
    try {
      const res = await fetch(candidate, { method: 'HEAD'});  // Agora deve encontrar!
      fileExists = res.ok;
    } catch (e) {
      fileExists = false;
    }

    function playTTS(){
      btn.disabled = true; btn.style.opacity = '0.6';
      playDialogue(a.Dialogo, ()=> {
        enableContinue();
        btn.disabled = false; btn.style.opacity = '1';
      });
    }

    if(fileExists){
      const audio = new Audio(candidate);
      audio.preload = 'auto';
      btn.onclick = () => {
        btn.disabled = true; btn.style.opacity = '0.6';
        audio.currentTime = 0;
        audio.play().catch(()=> {
          // se falhar ao reproduzir, tenta fallback para TTS
          playTTS();
        });
      };
      audio.onended = () => { enableContinue(); btn.disabled = false; btn.style.opacity = '1'; };
      audio.onerror = () => { playTTS(); };
    } else {
      btn.onclick = playTTS;
    }

    return;
  }

if (current.Atividade === 'CacaPalavras') {
  const c = current.Detalhes.CacaPalavras;
  activityBox.append(el('p',null,'Tema: ' + c.Tema));
  activityBox.append(el('p',null,'Encontre as palavras abaixo:'));
  const wordList = el('div','word-list');
  c.Palavras.forEach(w=>{ wordList.append(el('span','word-item', w)) });
  activityBox.append(wordList);

  const size = 12;
  
  // Cria grade vazia (vamos preencher depois)
  const grid = Array.from({length: size}, () => Array(size).fill(null));
  
  // Função para verificar se podemos colocar uma palavra
  function canPlaceWord(word, row, col, direction) {
    if (direction === 'h') {
      if (col + word.length > size) return false;
      for (let i = 0; i < word.length; i++) {
        if (grid[row][col + i] !== null && grid[row][col + i] !== word[i]) {
          return false;
        }
      }
    } else { // vertical
      if (row + word.length > size) return false;
      for (let i = 0; i < word.length; i++) {
        if (grid[row + i][col] !== null && grid[row + i][col] !== word[i]) {
          return false;
        }
      }
    }
    return true;
  }

  // Função para colocar uma palavra na grade
  function placeWord(word, row, col, direction) {
    for (let i = 0; i < word.length; i++) {
      if (direction === 'h') {
        grid[row][col + i] = word[i];
      } else {
        grid[row + i][col] = word[i];
      }
    }
  }

  // Embaralha as palavras para tentar colocar em ordem aleatória
  const shuffledWords = [...c.Palavras].sort(() => Math.random() - 0.5);
  
  // Tenta colocar cada palavra
  shuffledWords.forEach(word => {
    const upperWord = word.toUpperCase().replace(/\s/g, '');
    const directions = ['h', 'v'];
    let placed = false;
    
    // Tenta diferentes posições e direções
    for (let attempt = 0; attempt < 100 && !placed; attempt++) {
      const direction = directions[Math.floor(Math.random() * directions.length)];
      let row, col;
      
      if (direction === 'h') {
        row = Math.floor(Math.random() * size);
        col = Math.floor(Math.random() * (size - upperWord.length + 1));
      } else {
        row = Math.floor(Math.random() * (size - upperWord.length + 1));
        col = Math.floor(Math.random() * size);
      }
      
      if (canPlaceWord(upperWord, row, col, direction)) {
        placeWord(upperWord, row, col, direction);
        placed = true;
      }
    }
    
    if (!placed) {
      console.warn(`Não foi possível colocar: ${word}`);
    }
  });

  // Preenche células vazias com letras aleatórias
  for (let r = 0; r < size; r++) {
    for (let c = 0; c < size; c++) {
      if (grid[r][c] === null) {
        grid[r][c] = String.fromCharCode(65 + Math.floor(Math.random() * 26));
      }
    }
  }

  // O restante do código para criar a visualização permanece igual
  const gridEl = el('div','wordgrid');
  gridEl.style.display = 'grid';
  gridEl.style.gridTemplateColumns = `repeat(${size}, 28px)`;
  gridEl.style.gridAutoRows = '28px';
  gridEl.style.gap = '2px';
  gridEl.style.justifyContent = 'center';
  gridEl.style.margin = '20px 0';
  
  // Cria as células da grade
  for(let r = 0; r < size; r++){
    for(let cidx = 0; cidx < size; cidx++){
      const cell = el('div','grid-cell', grid[r][cidx]);
      cell.dataset.r = r; 
      cell.dataset.c = cidx;
      cell.tabIndex = 0;
      
      // Estilos da célula
      cell.style.width = '28px';
      cell.style.height = '28px';
      cell.style.display = 'flex';
      cell.style.alignItems = 'center';
      cell.style.justifyContent = 'center';
      cell.style.border = '1px solid #666';
      cell.style.borderRadius = '3px';
      cell.style.cursor = 'pointer';
      cell.style.userSelect = 'none';
      cell.style.fontWeight = '600';
      cell.style.fontSize = '14px';
      cell.style.background = '#f8f9fa';
      cell.style.transition = 'all 0.2s ease';
      
      cell.setAttribute('aria-label', `Letra ${grid[r][cidx]}, posição ${r + 1},${cidx + 1}`);
      
      // Eventos de teclado
      cell.addEventListener('keydown', (e)=>{
        if(e.key === 'Enter' || e.key === ' ') { 
          e.preventDefault(); 
          cell.click(); 
        }
      });
      
      // Efeitos hover
      cell.addEventListener('mouseenter', () => {
        if (!cell.classList.contains('found')) {
          cell.style.background = '#e9ecef';
          cell.style.transform = 'scale(1.05)';
        }
      });
      
      cell.addEventListener('mouseleave', () => {
        if (!cell.classList.contains('found') && !cell.classList.contains('selected')) {
          cell.style.background = '#f8f9fa';
          cell.style.transform = 'scale(1)';
        }
      });
      
      gridEl.append(cell);
    }
  }
  
  activityBox.append(gridEl);

  // Sistema de seleção
  const targets = c.Palavras.map(w => w.toUpperCase().replace(/\s/g, ''));
  let selectedCells = [];
  let isSelecting = false;

  function areCellsAdjacent(cell1, cell2) {
    const r1 = parseInt(cell1.dataset.r, 10);
    const c1 = parseInt(cell1.dataset.c, 10);
    const r2 = parseInt(cell2.dataset.r, 10);
    const c2 = parseInt(cell2.dataset.c, 10);
    
    const rowDiff = Math.abs(r1 - r2);
    const colDiff = Math.abs(c1 - c2);
    
    return (rowDiff <= 1 && colDiff <= 1) && !(rowDiff === 0 && colDiff === 0);
  }

  function isConsistentDirection(newCell) {
    if (selectedCells.length < 2) return true;
    
    const first = selectedCells[0];
    const last = selectedCells[selectedCells.length - 1];
    const newR = parseInt(newCell.dataset.r, 10);
    const newC = parseInt(newCell.dataset.c, 10);
    const lastR = parseInt(last.dataset.r, 10);
    const lastC = parseInt(last.dataset.c, 10);
    
    const deltaR = lastR - parseInt(first.dataset.r, 10);
    const deltaC = lastC - parseInt(first.dataset.c, 10);
    
    const dirR = deltaR === 0 ? 0 : deltaR / Math.abs(deltaR);
    const dirC = deltaC === 0 ? 0 : deltaC / Math.abs(deltaC);
    
    const newDeltaR = newR - lastR;
    const newDeltaC = newC - lastC;
    
    return (newDeltaR === dirR && newDeltaC === dirC) || 
           (selectedCells.length === 1);
  }

  function getCurrentWord() {
    return selectedCells.map(cell => cell.textContent.trim()).join('');
  }

  function checkForWord() {
    const currentWord = getCurrentWord();
    const currentWordReversed = currentWord.split('').reverse().join('');
    
    if (targets.includes(currentWord) || targets.includes(currentWordReversed)) {
      const foundWord = targets.includes(currentWord) ? currentWord : currentWordReversed;
      
      selectedCells.forEach(cell => {
        cell.classList.remove('selected');
        cell.classList.add('found');
        cell.style.background = '#4CAF50';
        cell.style.color = 'white';
        cell.style.borderColor = '#388E3C';
      });
      
      Array.from(wordList.querySelectorAll('.word-item')).forEach(item => {
        if (item.textContent.trim().toUpperCase().replace(/\s/g, '') === foundWord) {
          item.classList.add('word-found');
          item.style.textDecoration = 'line-through';
          item.style.color = '#4CAF50';
          item.style.fontWeight = 'bold';
        }
      });
      
      selectedCells = [];
      
      const allFound = targets.every(word => 
        Array.from(wordList.querySelectorAll('.word-item')).some(item => 
          item.classList.contains('word-found')
        )
      );
      
      if (allFound) {
        enableContinue();
      }
      
      return true;
    }
    
    // Se não formou uma palavra, limpa a seleção
    selectedCells.forEach(cell => {
      cell.classList.remove('selected');
      if (!cell.classList.contains('found')) {
        cell.style.background = '#f8f9fa';
        cell.style.color = 'inherit';
      }
    });
    selectedCells = [];
    
    return false;
  }

  gridEl.addEventListener('mousedown', (ev) => {
    const cell = ev.target.closest('.grid-cell');
    if (!cell || cell.classList.contains('found')) return;
    
    isSelecting = true;
    selectedCells = [cell];
    cell.classList.add('selected');
    cell.style.background = '#2196F3';
    cell.style.color = 'white';
  });

  gridEl.addEventListener('mouseover', (ev) => {
    if (!isSelecting) return;
    
    const cell = ev.target.closest('.grid-cell');
    if (!cell || cell.classList.contains('found') || selectedCells.includes(cell)) return;
    
    const lastCell = selectedCells[selectedCells.length - 1];
    if (areCellsAdjacent(lastCell, cell) && isConsistentDirection(cell)) {
      selectedCells.push(cell);
      cell.classList.add('selected');
      cell.style.background = '#2196F3';
      cell.style.color = 'white';
    }
  });

  document.addEventListener('mouseup', () => {
    if (isSelecting) {
      checkForWord();
      isSelecting = false;
    }
  });

  document.addEventListener('mousedown', (ev) => {
    if (!ev.target.closest('.wordgrid')) {
      selectedCells.forEach(cell => {
        cell.classList.remove('selected');
        if (!cell.classList.contains('found')) {
          cell.style.background = '#f8f9fa';
          cell.style.color = 'inherit';
        }
      });
      selectedCells = [];
      isSelecting = false;
    }
  });

  const style = document.createElement('style');
  style.textContent = `
    .word-found {
      text-decoration: line-through !important;
      color: #4CAF50 !important;
      font-weight: bold !important;
    }
    .grid-cell.found {
      background: #4CAF50 !important;
      color: white !important;
      border-color: #388E3C !important;
    }
    .grid-cell.selected {
      background: #2196F3 !important;
      color: white !important;
    }
    .word-list {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      justify-content: center;
      margin: 15px 0;
    }
    .word-item {
      padding: 5px 10px;
      background: #f0f0f0;
      border-radius: 15px;
      font-weight: 500;
    }
  `;
  document.head.append(style);

  return;
}
  activityBox.append(el('p',null,'Tipo de atividade desconhecido.'));
}

// --- TTS para diálogo de áudio (com callback onend) ---
function playDialogue(dialogo, onAllEnd){
  const utter = (text, onend)=>{
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'pt-BR';
    u.onend = onend;
    speechSynthesis.speak(u);
  };
  let idx = 0;
  const next = ()=> {
    if(idx >= dialogo.length){ if(onAllEnd) onAllEnd(); return; }
    const parte = dialogo[idx++];
    utter(parte.Personagem + ': ' + parte.Fala, next);
  };
  next();
}

// --- Summary (final da trilha) ---
function showSummary(stateKey){
  const state = JSON.parse(sessionStorage.getItem(stateKey) || '{}');
  const endTime = Date.now();
  const duration = state.startTime ? Math.floor((endTime - state.startTime)/1000) : 0;
  // modal simples
  const modal = el('div','summary-modal');
  const box = el('div','summary-box');
  box.append(el('h3',null,'Concluído'));
  box.append(el('p',null,`Atividades: ${state.completed || 0} / ${state.total || 0}`));
  box.append(el('p',null,`Erros: ${state.errors || 0}`));
  box.append(el('p',null,`Tempo: ${Math.floor(duration/60)}m ${duration%60}s`));
  const done = el('button','done-btn btn','Fechar');
  done.onclick = ()=> { sessionStorage.removeItem(stateKey); location.href = '/'; };
  box.append(done);
  modal.append(box);
  document.body.append(modal);
  // estilo inline mínimo para aparecer
  modal.style.position='fixed'; modal.style.left='0'; modal.style.top='0'; modal.style.right='0'; modal.style.bottom='0';
  modal.style.background='rgba(0,0,0,0.6)'; modal.style.display='flex'; modal.style.alignItems='center'; modal.style.justifyContent='center';
  box.style.background='#fff'; box.style.padding='20px'; box.style.borderRadius='8px'; box.style.minWidth='260px';
}

// --- Inicialização: decide página ---
(function(){
  if(document.getElementById('lessons')) renderIndex();
  const activityContainer = document.getElementById('activity-container');
  if(activityContainer){
    const codigo = window.codigo || (function(){ const p = location.pathname.split('/'); return p[p.length-1]; })();
    renderActivityPage(codigo);
  }
})();