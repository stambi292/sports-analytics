// Link-preview cards (1200x627, LinkedIn/Open Graph size) for every sports page.
// Add one entry per new project and run: node football/scripts/make_thumbnails.js
const {chromium}=require('playwright');
const T=[
 {f:'og-does-the-pitch-matter.png',bg:'#da291c',ink:'#fff',acc:'#fbe122',sub:'#ffe1dc',kick:'MAN UNITED · CLUB ACCOUNTS 2013/14–2025/26',t:'DOES THE PITCH<br><span>MATTER?</span>',
  body:`<div class="stats"><div><em class="a">+£59m</em><small>TV money, 15th to 3rd</small></div><div><em>−£29m</em><small>sponsorship since 2022/23</small></div><div><em>£449m</em><small>lost in 7 straight years</small></div></div>`},
 {f:'og-psg-from-stars-to-a-team.png',bg:'#004170',ink:'#fff',acc:'#da291c',sub:'#c7d9ea',kick:'PSG · CHAMPIONS LEAGUE · 2017–2026',t:'FROM STARS<br><span>TO A TEAM</span>',
  body:`<div class="stats"><div><em>0 in 7</em><small>with Neymar + Mbappé</small></div><div><em class="a">2 in 2</em><small>since, back to back</small></div><div><em>10 of 10</em><small>knockout ties won</small></div></div>`},
 {f:'og-the-spanish-school.png',bg:'#ffc400',ink:'#2a1a00',acc:'#c60b1e',sub:'#5a3b00',kick:'SPANISH COACHES · 2000–2026',t:'THE SPANISH<br><span>SCHOOL</span>',
  body:`<div class="stats"><div><em>9 of 27</em><small>Champions Leagues</small></div><div><em class="a">5 of 10</em><small>Euros and World Cups</small></div><div><em>10×</em><small>England's top coaches (2013)</small></div></div>`},
 {f:'og-peps-student.png',bg:'#db0007',ink:'#fff',acc:'#ffffff',sub:'#ffe1e1',kick:'ARSENAL · ARTETA VS GUARDIOLA · 2016–2026',t:"PEP'S STUDENT<br><span>NFL PLAYBOOK</span>",
  body:`<div class="stats"><div><em>19</em><small>corner goals, a record</small></div><div><em>46%</em><small>of wins by one goal (City 30%)</small></div><div><em>0</em><small>corner goals after the crackdown</small></div></div>`},
 {f:'og-why-spain.png',bg:'#c60b1e',ink:'#fff',acc:'#ffc400',sub:'#ffe9b0',kick:'SPAIN NATIONAL TEAM · EVERY RESULT SINCE 1990',t:'WHY SPAIN<br><span>THE BEST IN THE WORLD</span>',
  body:`<div class="stats"><div><em>44</em><small>competitive games unbeaten</small></div><div><em class="a">2358</em><small>Elo, number one</small></div><div><em>1 in 18</em><small>defeats vs the top 10</small></div></div>`},
 {f:'og-follow-the-money.png',bg:'#0d2148',ink:'#fff',acc:'#fdc301',sub:'#c8d4ea',kick:'UEFA NATIONS LEAGUE · MONEY AND GAMES · 2010–2025',t:'FOLLOW THE<br><span>MONEY</span>',
  body:`<div class="stats"><div><em>€484m</em><small>a season, up from €258m</small></div><div><em class="a">92%</em><small>paid to the 55 associations</small></div><div><em>−40%</em><small>friendlies</small></div></div>`},
 {f:'og-the-115.png',bg:'#6cabdd',ink:'#1c2c5b',acc:'#ffffff',sub:'#1c2c5b',kick:'PREMIER LEAGUE · MANCHESTER CITY · 115 CHARGES',t:'THE 115<br><span>WHAT COULD IT COST CITY?</span>',
  body:`<div class="stats"><div><em class="a">5 of 8</em><small>titles a 3-point penalty flips</small></div><div><em>−6</em><small>Everton, for one breach</small></div><div><em>3rd → 20th</em><small>City now, at −15</small></div></div>`},
 {f:'og-where-did-germanys-talent-go.png',bg:'#ffffff',ink:'#111111',acc:'#111111',sub:'#555555',kick:'GERMANY · GOLDEN ERA VS TODAY · 2014/15–2023/24',t:"WHERE DID GERMANY'S<br><span>TALENT GO?</span>",
  body:`<div class="stats"><div><em class="a">26 → 7</em><small>future stars, 2017/18 vs 2021/22</small></div><div><em>1.7 vs 10.2</em><small>world-class full-backs a season, GER vs ESP</small></div></div>`},
 {f:'og-the-poacher.png',bg:'#1d9053',ink:'#fff',acc:'#0b3d22',sub:'#d7f5e3',kick:'BUNDESLIGA 2026/27 · NICLAS FÜLLKRUG, WERDER BREMEN',t:'THE POACHER<br><span>PEAK OR FLUKE?</span>',
  body:`<div class="stats"><div><em>9 in 8</em><small>league goals this season</small></div><div><em class="a">54 vs 49.4</em><small>Bundesliga goals vs xG</small></div><div><em>1 vs 4.4</em><small>abroad, 2025/26</small></div></div>`},
 {f:'og-the-injury-bill.png',bg:'#0e1f3d',ink:'#fff',acc:'#ff6b7c',sub:'#b8c5dc',kick:'BUNDESLIGA · WAGES PAID TO INJURED PLAYERS, 2024/25',t:'THE INJURY<br><span>BILL</span>',
  body:`<div class="stats"><div><em class="a">€110.9m</em><small>wages to injured players</small></div><div><em>23%</em><small>of it was Bayern's</small></div><div><em>31 days</em><small>Hoffenheim's average absence</small></div></div>`},
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
