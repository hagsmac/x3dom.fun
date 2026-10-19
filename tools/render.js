// Screenshots the X_ITE pages at 2 timestamps, checks non-blank + differ. Serves the folder on 127.0.0.1 only; the X_ITE CDN URL
// (cdn.jsdelivr.net/npm/x_ite@16.4.3/dist/...) is answered from the local dist, every other external request is aborted.
//   NODE_PATH=/tmp/node_modules CHROME_PATH=<chromium> XITE_DIST=/tmp/xite-pack/pkg/package/dist node tools/render.js [scene ...]
const http=require('http'),fs=require('fs'),path=require('path');const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..'),dist=process.env.XITE_DIST;
const all=['flywheel','galaxy','sierpinski','equalizer','cradle','whack','tunnel','solar','bounce','touch'];const scenes=process.argv.slice(2).length?process.argv.slice(2):all;
const clickAt={touch:[0.5,0.5],whack:[0.5,0.55]};
const mime={'.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.x3d':'model/x3d+xml','.html':'text/html','.json':'application/json','.woff2':'font/woff2','.png':'image/png'};
const srv=http.createServer((q,r)=>{const f=path.join(root,decodeURIComponent(q.url.split('?')[0]));if(!f.startsWith(root)||!fs.existsSync(f)||fs.statSync(f).isDirectory()){r.writeHead(404);return r.end();}r.writeHead(200,{'content-type':mime[path.extname(f)]||'application/octet-stream'});fs.createReadStream(f).pipe(r);});
(async()=>{await new Promise(r=>srv.listen(0,'127.0.0.1',r));const port=srv.address().port;
const b=await chromium.launch({executablePath:process.env.CHROME_PATH,headless:true,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--no-sandbox']});
const res={};
try{for(const n of scenes){const p=await b.newPage({viewport:{width:1100,height:720}});const logs=[];
await p.route(/^https?:\/\/(?!127\.0\.0\.1)/,rt=>{const u=rt.request().url();const m=u.match(/^https:\/\/cdn\.jsdelivr\.net\/npm\/x_ite@16\.4\.3\/dist\/(.*?)(\?.*)?$/);
 if(m){const f=path.join(dist,m[1]);if(fs.existsSync(f)&&fs.statSync(f).isFile())return rt.fulfill({body:fs.readFileSync(f),contentType:mime[path.extname(f)]||'application/octet-stream'});}
 logs.push('blocked '+u.slice(0,100));rt.abort();});
p.on('console',m=>{if(['error','warning'].includes(m.type()))logs.push(m.text().slice(0,200))});p.on('pageerror',e=>logs.push('pageerror '+e.message));
p.on('response',r=>{if(r.status()>=400)logs.push('http '+r.status()+' '+r.url().slice(0,100))});
const t0=Date.now();await p.goto(`http://127.0.0.1:${port}/pages/${n}.xite.html`);
await p.waitForFunction(()=>{const x=document.getElementById('c').browser;return x&&x.currentScene&&x.currentScene.rootNodes.length>0},null,{timeout:90000});
const loadMs=Date.now()-t0;await p.waitForTimeout(1200);
const el=p.locator('#c');
const stat=async f=>{const buf=await el.screenshot({path:f});const d='data:image/png;base64,'+buf.toString('base64');return p.evaluate(async d=>{const i=new Image();i.src=d;await i.decode();const c=document.createElement('canvas');c.width=i.width;c.height=i.height;const x=c.getContext('2d');x.drawImage(i,0,0);const px=x.getImageData(0,0,c.width,c.height).data;const set=new Set();for(let k=0;k<px.length;k+=40)set.add(px[k]>>4<<8|px[k+1]>>4<<4|px[k+2]>>4);return {colors:set.size,px:Array.from(px)}},d)};
const a=await stat(`shots/${n}-t1.png`);
if(clickAt[n]){const bb=await el.boundingBox();await p.mouse.click(bb.x+bb.width*clickAt[n][0],bb.y+bb.height*clickAt[n][1]);await p.waitForTimeout(450);}else await p.waitForTimeout(1300);
const c=await stat(`shots/${n}-t2.png`);
let diff=0;for(let k=0;k<a.px.length;k+=4)if(Math.abs(a.px[k]-c.px[k])+Math.abs(a.px[k+1]-c.px[k+1])+Math.abs(a.px[k+2]-c.px[k+2])>30)diff++;
res[n]={loadMs,colors1:a.colors,colors2:c.colors,diffPct:+(100*diff/(a.px.length/4)).toFixed(2),logs};console.log(n,JSON.stringify(res[n]));await p.close();}}
finally{await b.close();srv.close();}
fs.writeFileSync(path.join(root,'validation/render.json'),JSON.stringify(res,null,1));})();
