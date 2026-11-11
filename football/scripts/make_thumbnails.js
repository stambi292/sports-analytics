// Link-preview cards (1200x627, LinkedIn/Open Graph size) for every sports page.
// Add one entry per new project and run: node football/scripts/make_thumbnails.js
const {chromium}=require('playwright');
const T=[
 {f:'og-did-the-money-buy-points.png',bg:'#0f2a1f',ink:'#fff',acc:'#3fcf86',sub:'#b9cfc3',kick:'BUNDESLIGA 2026/27 · SUMMER SPENDING VS POINTS AFTER 9 GAMES',t:'DID THE MONEY<br><span>BUY POINTS?</span>',
  body:`<div class="stats"><div><em>€782m</em><small>spent this summer</small></div><div><em class="a">€0.49m</em><small>Werder, per point</small></div><div><em style="color:#f07a5f">€9.81m</em><small>Leverkusen, per point</small></div></div>`},
 {f:'og-is-frankfurt-in-crisis.png',bg:'#e1000f',ink:'#fff',acc:'#111111',sub:'#ffe3e5',kick:'BUNDESLIGA 2026/27 · EINTRACHT FRANKFURT AFTER 9 GAMES',t:'IS FRANKFURT<br><span>IN CRISIS?</span>',
  body:`<div class="stats"><div><em>12</em><small>points after 9</small></div><div><em class="a">20</em><small>goals conceded, most since 2010</small></div><div><em>1 in 3</em><small>with this start still made top 6</small></div></div>`},
 {f:'og-when-a-player-collapses.png',bg:'#141a22',ink:'#fff',acc:'#f0595d',sub:'#b7c0cc',kick:'SUDDEN DEATH IN FOOTBALL · FIFA REGISTRY 2014–18',t:'WHEN A PLAYER<br><span>COLLAPSES</span>',
  body:`<div class="stats"><div><em>617</em><small>players, 67 countries</small></div><div><em>35%</em><small>survived with bystander CPR</small></div><div><em style="color:#3ccf84">85%</em><small>survived with trained staff + AED</small></div></div>`},
 {f:'og-home.png',bg:'#0f3d2a',ink:'#fff',acc:'#2dd4bf',sub:'#bcd3c6',kick:'SPORTS ANALYTICS · BY STEPHEN tAMBI',t:'SPORTS,<br><span>THROUGH DATA</span>',
  body:`<div class="stats"><div><em>3</em><small>interactive projects</small></div><div><em class="a">Football</em><small>first, more sports next</small></div></div>`},
 {f:'og-price-of-a-title.png',bg:'#0f3d2a',ink:'#fff',acc:'#d4a017',sub:'#bcd3c6',kick:"WAGES VS RESULTS · EUROPE'S TOP 5 LEAGUES",t:'THE PRICE OF<br><span>A TITLE</span>',
  body:`<div class="vs"><div><b>LEVERKUSEN</b><small>Champions · unbeaten</small><em class="a">€192m</em></div><i>vs</i><div><b>BAYERN</b><small>3rd place</small><em>€430m</em></div></div>`},
 {f:'og-leverkusen.png',bg:'#0b0b0b',ink:'#fff',acc:'#e32221',sub:'#c9c9c9',kick:'BUNDESLIGA 2023/24 · BAYER 04 LEVERKUSEN',t:'UNBEATEN, <span>BY THE<br>LAST MINUTE</span>',
  body:`<div class="stats"><div><em>28</em><small>wins</small></div><div><em>6</em><small>draws</small></div><div><em class="a">0</em><small>defeats</small></div><div><em class="a">13</em><small>goals after 85'</small></div></div>`},
 {f:'og-premier-league.png',bg:'#0e1a2b',ink:'#fff',acc:'#4a90e8',sub:'#b9c6d8',kick:'PREMIER LEAGUE · 15 SEASONS · 5,700 MATCHES',t:'PREMIER LEAGUE<br><span>BY THE NUMBERS</span>',
  body:`<div class="stats"><div><em>15</em><small>seasons</small></div><div><em>5,700</em><small>matches</small></div><div><em class="a">2010–25</em><small>title races</small></div></div>`},
];
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1200,height:627},deviceScaleFactor:1});
for(const x of T){await p.setContent(`<html><body style="margin:0;width:1200px;height:627px;background:${x.bg};color:${x.ink};font-family:Inter,sans-serif;overflow:hidden;position:relative">
<div style="position:absolute;left:0;right:0;bottom:0;height:14px;background:${x.acc}"></div>
<div style="box-sizing:border-box;height:615px;padding:36px 84px;display:flex;flex-direction:column;justify-content:center;gap:22px">
<div style="font:700 24px Inter;letter-spacing:.12em;color:${x.sub}">${x.kick}</div>
<div style="font:800 96px/0.95 'Inter Display',Inter;letter-spacing:-.01em">${x.t.replace(/<span>/g,`<span style="color:${x.acc}">`)}</div>
<style>.vs{display:flex;gap:28px;align-items:center;margin-top:18px}.vs>div{background:rgba(255,255,255,.08);border-radius:14px;padding:22px 30px;display:flex;flex-direction:column;gap:4px;min-width:300px}
b{font:800 32px Inter}small{font:500 22px Inter;color:${x.sub}}em{font:800 62px Inter;font-style:normal}em.a{color:${x.acc}}i{font:700 30px Inter;color:${x.sub};font-style:normal}
.stats{display:flex;gap:64px;margin-top:22px}.stats>div{display:flex;flex-direction:column}</style>${x.body}
<div style="font:500 22px Inter;color:${x.sub};margin-top:8px">By Stephen tAMBI</div></div></body></html>`);
await p.screenshot({path:require('path').join(__dirname,'../../images',x.f)});}
await b.close()})();
