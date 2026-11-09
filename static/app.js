// CSRF token into every POST form
const tok=document.querySelector('meta[name=csrf]').content;
document.querySelectorAll('form[method=post]').forEach(f=>{if(!f.querySelector('[name=_csrf]')){const i=document.createElement('input');i.type='hidden';i.name='_csrf';i.value=tok;f.appendChild(i)}});
// OTP boxes
const ob=[...document.querySelectorAll('.ob')];
if(ob.length){const code=document.getElementById('code');const upd=()=>code.value=ob.map(b=>b.value).join('');
 ob.forEach((b,i)=>{b.addEventListener('input',()=>{b.value=b.value.replace(/\D/g,'');if(b.value&&ob[i+1])ob[i+1].focus();upd()});
  b.addEventListener('keydown',e=>{if(e.key==='Backspace'&&!b.value&&ob[i-1])ob[i-1].focus()});
  b.addEventListener('paste',e=>{const d=(e.clipboardData.getData('text')||'').replace(/\D/g,'').slice(0,6);if(d){e.preventDefault();d.split('').forEach((c,j)=>ob[j]&&(ob[j].value=c));upd()}})});ob[0].focus()}
// password eye
document.querySelectorAll('.eye').forEach(b=>b.addEventListener('click',()=>{const i=b.parentElement.querySelector('input');i.type=i.type==='password'?'text':'password'}));
// translation toggle (original <-> translated)
document.querySelectorAll('.tr-toggle').forEach(a=>a.addEventListener('click',e=>{e.preventDefault();const b=a.closest('.b'),s=b.querySelector('.shown'),o=b.querySelector('.orig');
 const showOrig=o.hidden;o.hidden=!showOrig;s.hidden=showOrig;a.textContent=showOrig?a.dataset.b:a.dataset.a}));
// voice search (Web Speech API, editable text, live words)
const mic=document.getElementById('mic');
if(mic){const R=window.SpeechRecognition||window.webkitSpeechRecognition;mic.addEventListener('click',()=>{if(!R)return alert('Voice input is not supported in this browser (use Chrome/Edge).');
 const r=new R();r.lang=document.documentElement.lang==='ur'?'ur-PK':'en-US';r.interimResults=true;const q=document.getElementById('q');
 r.onresult=e=>{q.value=[...e.results].map(x=>x[0].transcript).join(' ')};r.start()})}
// scroll chat to bottom
const m=document.getElementById('msgs');if(m)window.scrollTo(0,document.body.scrollHeight);
