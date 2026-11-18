/* Stewart on Immigration — interações compartilhadas (tema, progresso, share, reveal). */
(function(){
  var root=document.documentElement, tkey='soi-theme';
  root.classList.add('js');
  var SUN='<circle cx="12" cy="12" r="4.5"/><path d="M12 2v2.5M12 19.5V22M4.2 4.2l1.8 1.8M18 18l1.8 1.8M2 12h2.5M19.5 12H22M4.2 19.8l1.8-1.8M18 6l1.8-1.8"/>';
  var MOON='<path d="M21 12.8A8.5 8.5 0 1 1 11.2 3a6.6 6.6 0 0 0 9.8 9.8z"/>';
  function get(){var t=null;try{t=localStorage.getItem(tkey)}catch(e){} return t||'light';}
  function apply(t){root.setAttribute('data-theme',t);var ic=document.getElementById('thIcon');if(ic)ic.innerHTML=(t==='dark')?SUN:MOON;}
  apply(get());
  var tb=document.getElementById('themeBtn');
  if(tb)tb.addEventListener('click',function(){var c=root.getAttribute('data-theme')==='dark'?'light':'dark';apply(c);try{localStorage.setItem(tkey,c)}catch(e){}});

  // barra: sombra ao rolar + progresso de leitura (página inteira, standalone)
  var bar=document.getElementById('ebar'), rp=document.getElementById('rprog');
  function onScroll(){
    var h=document.documentElement, sc=h.scrollTop||document.body.scrollTop, mx=(h.scrollHeight-h.clientHeight)||1;
    if(bar){ if(sc>6) bar.classList.add('scrolled'); else bar.classList.remove('scrolled'); }
    if(rp){ rp.style.width=(100*sc/mx)+'%'; }
  }
  window.addEventListener('scroll',onScroll,{passive:true}); onScroll();

  // toast
  var toast=document.createElement('div'); toast.className='toast'; document.body.appendChild(toast); var tt;
  function say(m){toast.textContent=m;toast.classList.add('on');clearTimeout(tt);tt=setTimeout(function(){toast.classList.remove('on')},1800);}
  window.__soiToast=say;

  // menu compartilhar
  var sb=document.getElementById('shareBtn'), menu=document.getElementById('shMenu');
  function cur(){return {u:location.href,t:document.title};}
  if(sb&&menu){
    sb.addEventListener('click',function(e){e.stopPropagation();var x=cur();
      var li=menu.querySelector('[data-sh=li]'); if(li) li.href='https://www.linkedin.com/sharing/share-offsite/?url='+encodeURIComponent(x.u);
      var wa=menu.querySelector('[data-sh=wa]'); if(wa) wa.href='https://wa.me/?text='+encodeURIComponent(x.t+' '+x.u);
      menu.classList.toggle('on');});
    var cp=menu.querySelector('[data-sh=copy]');
    if(cp) cp.addEventListener('click',function(){var x=cur();
      if(navigator.share){navigator.share({title:x.t,url:x.u}).catch(function(){});}
      else if(navigator.clipboard){navigator.clipboard.writeText(x.u).then(function(){say('Link copiado')},function(){say(x.u)});}
      else say(x.u); menu.classList.remove('on');});
    document.addEventListener('click',function(){menu.classList.remove('on');});
  }
  // botões "compartilhar" de card (data-share no card com data-url/data-title)
  document.querySelectorAll('[data-cardshare]').forEach(function(b){
    b.addEventListener('click',function(e){e.preventDefault();e.stopPropagation();
      var u=b.getAttribute('data-url')||location.href, t=b.getAttribute('data-title')||document.title;
      if(navigator.share){navigator.share({title:t,url:u}).catch(function(){});}
      else if(navigator.clipboard){navigator.clipboard.writeText(u).then(function(){say('Link copiado')},function(){say(u)});}
      else say(u);});
  });

  // reveal on scroll
  var els=[].slice.call(document.querySelectorAll('.reveal'));
  if('IntersectionObserver' in window && els.length){
    var io=new IntersectionObserver(function(es){es.forEach(function(en){if(en.isIntersecting){en.target.classList.add('in');io.unobserve(en.target);}})},{rootMargin:'0px 0px -8% 0px',threshold:.06});
    els.forEach(function(el){io.observe(el);});
  } else { els.forEach(function(el){el.classList.add('in');}); }

  // registra leitura (conveniência local)
  try{var slug=location.pathname.split('/').pop();localStorage.setItem('soi-last',JSON.stringify({u:slug,t:document.title,ts:Date.now()}));}catch(e){}
})();
