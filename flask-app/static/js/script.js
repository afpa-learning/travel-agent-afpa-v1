// --- Theme toggle ---------------------------------------------------------
const themeSwitch = document.getElementById('themeSwitch');
const root = document.documentElement;

function applyTheme(isLight){
  root.setAttribute('data-theme', isLight ? 'light' : 'dark');
  themeSwitch.checked = isLight;
}
applyTheme(false); // sombre par défaut, à l'image de la maquette d'origine

themeSwitch.addEventListener('change', () => applyTheme(themeSwitch.checked));

// --- Chat logic -------------------------------------------------------------
const chatScroll = document.getElementById('chatScroll');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const newConversation = document.getElementById('newConversation');

const converter = new showdown.Converter();

function scrollDown(){
  chatScroll.scrollTop = chatScroll.scrollHeight;
}

function addUserMessage(text){
  const div = document.createElement('div');
  div.className = 'msg user';
  div.textContent = text;
  chatScroll.appendChild(div);
  scrollDown();
}

function addSystemNotice(text){
  const div = document.createElement('div');
  div.className = 'msg system';
  div.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg><span>${text}</span>`;
  chatScroll.appendChild(div);
  scrollDown();
}

function addAssistantHTML(innerHTML){
  const div = document.createElement('div');
  div.className = 'msg assistant';
  div.innerHTML = innerHTML;
  chatScroll.appendChild(div);
  scrollDown();
}

function showTyping(){
  const div = document.createElement('div');
  div.className = 'typing';
  div.id = 'typingIndicator';
  div.innerHTML = '<span></span><span></span><span></span>';
  chatScroll.appendChild(div);
  scrollDown();
  return div;
}

function clearConversation() {
  chatScroll.innerHTML="";
  chatInput.value='';
  scrollDown();
  fetchApiClearHistory();
  chatInput.focus();
}

const QUESTIONS = {
  "search-paris-tokyo": "Trouves-moi un vol Paris → Tokyo fin novembre, budget max 700 €",
  "search-lisbonne": "Quels sont les vols directs vers Lisbonne en octobre ?",
  "compare-flights": "Compare les vols AF1180 et EK071",
  "search-bangkok": "Quel est le vol le moins cher pour Bangkok en décembre ?",
  "count-places": "Combien de places restent sur le vol AF1180 du 10 décembre ?"
};

function handleSend(text){
  if(!text) return;
  addUserMessage(text);
  chatInput.value = '';
  fetchAsk(text);
}

newConversation.addEventListener('click', () => clearConversation());

sendBtn.addEventListener('click', () => handleSend(chatInput.value.trim()));
chatInput.addEventListener('keydown', (e) => {
  if(e.key === 'Enter') handleSend(chatInput.value.trim());
});

document.querySelectorAll('.suggestion').forEach(btn => {
  btn.addEventListener('click', () => {
    
    clearConversation();
    const key = btn.dataset.q;
    handleSend(QUESTIONS[key]);
  });
});

async function fetchCallTool() {
  try {
    const res = await fetch("/api/call", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tool_name: "search_flights",
        arguments: { origin: "CDG", destination: "HND" }
      })
    });
    const data = await res.json();
    console.log(data);
  } catch (error) {
      const t = document.getElementById('typingIndicator');
      if(t) t.remove();
      addSystemNotice("Erreur lors de la récupération : "+error);
  }
}

function cleanResponse(text) {
  text=text.replaceAll("| | |\n|---|---|\n| ",""); 
  text=text.replaceAll("|\n\n","<br><br>");
  text=text.replaceAll("|\n|","<br>"); 
  text=text.replaceAll("|",":");
  
  return text;
}

async function fetchAsk(demand) {
  showTyping();
  try {
    const res = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: demand
      })
    });
    const data = await res.json();
    
    const html = converter.makeHtml(cleanResponse(data.reply));
    addAssistantHTML(html);
    const t = document.getElementById('typingIndicator');
    if(t) t.remove();
    return data;
  } catch (error) {
      const t = document.getElementById('typingIndicator');
      if(t) t.remove();
      addSystemNotice("Erreur lors de la récupération : "+error);
  }
}

async function fetchApiClearHistory() {
   try {
       const response = await fetch("/api/history/reset");
       if (!response.ok) {
           addSystemNotice(`Erreur HTTP : ${response.status}`);
       }
       const data = await response.json();
   } catch (error) {
       addSystemNotice("Erreur lors de la récupération : "+error);
   }
} 
async function fetchApiStatus() {
   try {
       const response = await fetch("/api/status");
       if (!response.ok) {
           addSystemNotice(`Erreur HTTP : ${response.status}`);
       }
       const data = await response.json();
       
      if (data.mcp_connected=="False") {
        document.getElementById("connectedMcp").classList.remove("ok");
        document.getElementById("connectedMcp").classList.add("error");
        document.getElementById("connectedMcp").innerHTML='<span class="dot"></span>MCP: déconnecté';
      } else {
        document.getElementById("connectedMcp").classList.remove("error");
        document.getElementById("connectedMcp").classList.add("ok");
        document.getElementById("connectedMcp").innerHTML='<span class="dot"></span>MCP: connecté';
      }
      if (data.llm_connected=="False") {
        document.getElementById("connectedLLM").classList.remove("ok");
        document.getElementById("connectedLLM").classList.add("error");
        document.getElementById("connectedLLM").innerHTML='<span class="dot"></span>LLM: déconnecté';
      } else {
        document.getElementById("connectedLLM").classList.remove("error");
        document.getElementById("connectedLLM").classList.add("ok");
        document.getElementById("connectedLLM").innerHTML='<span class="dot"></span>LLM: connecté';
      }


      if (data.tools !=null) {
         document.getElementById("toolsList").innerHTML="";
          data.tools.forEach((tool, index) => {
              document.getElementById("toolsList").innerHTML+='<div class="tool-item tooltip"><span class="dot"></span>'+tool.name+'<span class="tooltiptext">'+tool.description+'</span></div>';
              
            });
      } 
      
      addUserMessage(QUESTIONS["search-paris-tokyo"]);
      fetchAsk(QUESTIONS["search-paris-tokyo"]);
      fetchCallTool();

   } catch (error) {
       addSystemNotice("Erreur lors de la récupération : "+error);
   }
}
fetchApiStatus();

