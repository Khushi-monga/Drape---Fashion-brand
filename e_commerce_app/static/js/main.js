// ── Tab switching
function setTab(btn){
  document.querySelectorAll('.cat-tab').forEach(t=>{
    t.classList.remove('active');t.setAttribute('aria-selected','false')
  });
  btn.classList.add('active');btn.setAttribute('aria-selected','true');
}

// ── Search bar: show suggestions on focus
const searchBar=document.getElementById('navSearchBar');
const searchInput=document.getElementById('searchInput');
searchInput.addEventListener('focus',()=>searchBar.classList.add('active'));
searchInput.addEventListener('blur',()=>setTimeout(()=>searchBar.classList.remove('active'),180));
searchInput.addEventListener('keydown',e=>{if(e.key==='Escape'){searchInput.blur();searchInput.value=''}});

// ── Scroll reveal with directional classes
const revObs=new IntersectionObserver(entries=>{
  entries.forEach(e=>{
    if(e.isIntersecting){
      e.target.classList.add('visible');
      revObs.unobserve(e.target);
    }
  });
},{threshold:.1,rootMargin:'0px 0px -40px 0px'});
document.querySelectorAll('.reveal').forEach(el=>revObs.observe(el));

// ── Hero parallax
const heroBg=document.getElementById('heroBg');
const heroTex=document.getElementById('heroTex');
const heroContent=document.getElementById('heroContent');
const navTop=document.getElementById('navTop');

function onScroll(){
  const y=window.scrollY;
  if(heroBg) heroBg.style.transform=`translateY(${y*.36}px)`;
  if(heroTex) heroTex.style.transform=`translateY(${y*.2}px)`;
  if(heroContent) heroContent.style.transform=`translateY(${y*.1}px)`;
  navTop.classList.toggle('scrolled',y>8);
}
window.addEventListener('scroll',onScroll,{passive:true});

// ── Reduced motion
if(window.matchMedia('(prefers-reduced-motion:reduce)').matches){
  document.querySelectorAll('.reveal').forEach(el=>el.classList.add('visible'));
  window.removeEventListener('scroll',onScroll);
}