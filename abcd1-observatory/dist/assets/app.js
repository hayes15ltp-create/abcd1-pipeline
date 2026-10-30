const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const escape = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const labels = {overview:'Overview',workstreams:'Vector workstreams',roadmap:'Roadmap',registry:'Tests & predictions',tools:'Tool stack',resources:'Documents & sources'};
let project;
let milestoneFilter = 'all';
let toastTimer;
const includes = (value, query) => value.toLowerCase().includes(query.trim().toLowerCase());
const symbol = (stream) => `<span class="method-symbol ${escape(stream.color)}" aria-hidden="true">${escape(stream.symbol)}</span>`;
const safeUrl = (value) => { try { const url = new URL(value, window.location.href); return ['http:','https:'].includes(url.protocol) ? url.href : '#'; } catch { return '#'; } };

function showPage() {
  const requested = location.hash.slice(1);
  const page = Object.hasOwn(labels, requested) ? requested : 'overview';
  $$('.page').forEach(el => { el.hidden = el.id !== `page-${page}`; });
  $$('[data-page]').forEach(el => { const active = el.dataset.page === page; el.classList.toggle('active',active); active ? el.setAttribute('aria-current','page') : el.removeAttribute('aria-current'); });
  $('#page-label').textContent = labels[page];
  document.title = `${labels[page]} · ABCD1 Research Observatory`;
  $('#primary-nav').classList.remove('open');
  $('#menu-toggle').setAttribute('aria-expanded','false');
  if (requested && requested !== 'main') { window.scrollTo({top:0,behavior:'instant'}); $('#main').focus({preventScroll:true}); }
}

function notify(message) {
  const toast = $('#toast'); clearTimeout(toastTimer); toast.textContent = message; toast.hidden = false;
  toastTimer = setTimeout(() => { toast.hidden = true; }, 3500);
}

function download(name, value, type) {
  const url = URL.createObjectURL(new Blob([value],{type}));
  const link = document.createElement('a'); link.href = url; link.download = name; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function renderOverview() {
  const metrics = [
    {label:'Delivery workstreams',value:project.workstreams.length,note:'Research categories defined',icon:'⌘'},
    {label:'Study variants',value:project.cohort.imported ? project.cohort.variantCount : 'Not imported',note:'Pathogenic registry entries only',icon:'⋈',words:!project.cohort.imported},
    {label:'Published project runs',value:project.runs.length,note:'No findings implied by planning',icon:'▤'},
    {label:'Background research loop',value:project.automation.active ? 'Active' : 'Not active',note:'Hourly / daily cadence specified',icon:'↻',words:true}
  ];
  $('#metrics').innerHTML = metrics.map(m=>`<div class="metric"><div class="metric-top"><span>${escape(m.label)}</span><span class="metric-icon" aria-hidden="true">${m.icon}</span></div><div class="metric-value ${m.words?'words':''}">${escape(m.value)}</div><div class="metric-note">${escape(m.note)}</div></div>`).join('');
  $('#overview-streams').innerHTML = project.workstreams.map(s=>`<button class="stream-mini" data-stream="${escape(s.id)}" aria-label="Explore ${escape(s.name)}"><div class="mini-top">${symbol(s)}<span class="mini-arrow" aria-hidden="true">↗</span></div><h3>${escape(s.name)}</h3><p>${escape(s.summary)}</p><div class="mini-bottom"><span class="badge planned">Evidence review pending</span><span>${escape(s.familyLabel)}</span></div></button>`).join('');
  $('#pipeline').innerHTML = [{name:'Design',status:'Ready',done:true},{name:'Data',status:'Not imported'},{name:'Analysis',status:'Not published'},{name:'Validation',status:'Not recorded'}].map((p,i)=>`<div class="pipeline-stage ${p.done?'done':''}"><span class="stage-number">${p.done?'✓':i+1}</span><strong>${p.name}</strong><small>${p.status}</small></div>`).join('');
  $('#decisions').innerHTML = project.decisions.map(d=>`<div class="decision"><span class="decision-check" aria-hidden="true">✓</span><div><strong>${escape(d.title)}</strong><p>${escape(d.description)}</p></div></div>`).join('');
}

function renderStreams() {
  const query = $('#stream-search').value;
  const family = $('#family-filter').value;
  const streams = project.workstreams.filter(s => (family === 'all' || family === s.family) && includes([s.name,s.description,...s.tags,...s.questions].join(' '),query));
  $('#stream-count').textContent = `${streams.length} of ${project.workstreams.length} workstreams`;
  $('#stream-grid').innerHTML = streams.length ? streams.map(s=>`<article class="stream-card"><div class="stream-card-top">${symbol(s)}<span class="badge planned">Planned</span></div><div class="stream-card-copy"><span class="eyebrow">${escape(s.familyLabel)}</span><h2>${escape(s.name)}</h2><p>${escape(s.description)}</p><div class="stream-tags">${s.tags.map(t=>`<span class="tag">${escape(t)}</span>`).join('')}</div></div><div class="stream-card-bottom"><span>Evidence review pending</span><button data-stream="${escape(s.id)}">Open questions ↗</button></div></article>`).join('') : `<div class="empty-filter"><h3>No matching workstreams</h3><p>Try a broader search or choose another delivery family.</p></div>`;
}

function renderMilestones() {
  const complete = project.milestones.filter(m=>m.status==='complete').length;
  const planned = project.milestones.filter(m=>m.status==='planned').length;
  $('#roadmap-summary').innerHTML = `<div class="summary-box"><strong>${complete}</strong><span>planning checkpoints complete</span><p>Scope, tools, data rules, organization, and cadence specified.</p></div><div class="summary-box next"><strong>${planned}</strong><span>implementation milestones ahead</span><p>Each milestone requires its own documented outputs and checks.</p></div>`;
  $('#milestones').innerHTML = project.milestones.map((m,i)=>({m,i})).filter(({m})=>milestoneFilter==='all'||m.status===milestoneFilter).map(({m,i})=>`<article class="milestone"><span class="milestone-number ${m.status==='complete'?'done':''}" aria-hidden="true">${m.status==='complete'?'✓':String(i+1).padStart(2,'0')}</span><div><h3>${escape(m.title)}</h3><p>${escape(m.description)}</p></div><span class="badge ${escape(m.status)}">${m.status==='complete'?'Planning complete':escape(m.phase)+' · planned'}</span></article>`).join('');
}

function renderRuns() {
  const query = $('#run-search').value;
  const type = $('#evidence-filter').value;
  const rows = project.runs.filter(r=>(type==='all'||r.evidenceType===type)&&includes([r.id,r.variant,r.tool,r.endpoint,r.vectorMethod].join(' '),query));
  if (!project.runs.length) { $('#run-list').innerHTML = `<div class="registry-empty"><div class="empty-orbit" aria-hidden="true">▤</div><span class="eyebrow">A PLACE FOR EVERY RESULT</span><h2>The research record starts here.</h2><p>No project run records have been published in this snapshot. The database and its publication connection are planned. Predictions will be clearly distinguished from validated findings.</p><a href="#roadmap" class="button primary">See the implementation plan <span>→</span></a></div>`; return; }
  if (!rows.length) { $('#run-list').innerHTML = `<div class="empty-filter"><h3>No matching records</h3><p>Change the search or evidence filter.</p></div>`; return; }
  $('#run-list').innerHTML = `<div class="table-wrap"><table class="run-table"><thead><tr><th>Run</th><th>Variant</th><th>Method</th><th>Evidence</th><th>Status</th><th>Source</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${escape(r.id)}</td><td>${escape(r.variant)}</td><td>${escape(r.tool)}</td><td>${escape(r.evidenceType)}</td><td>${escape(r.status)}</td><td>${r.sourceUrl?`<a href="${escape(safeUrl(r.sourceUrl))}" target="_blank" rel="noopener noreferrer">Source ↗</a>`:'Not provided'}</td></tr>`).join('')}</tbody></table></div>`;
}

function renderTools() {
  const query = $('#tool-search').value;
  const tier = $('#tool-tier').value;
  const tools = project.tools.filter(t=>(tier==='all'||tier===t.tier)&&includes([t.name,t.stage,t.description].join(' '),query));
  $('#tool-count').textContent = `${tools.length} tools / tool groups`;
  $('#tool-list').innerHTML = tools.length ? tools.map(t=>`<article class="tool-card"><div class="tool-card-top"><h2>${escape(t.name)}</h2><span class="badge ${escape(t.tier)}">${t.tier==='core'?'Core':'Conditional'}</span></div><div class="tool-stage">${escape(t.stage)}</div><p>${escape(t.description)}</p><div class="tool-license">${escape(t.access)}</div><a href="${escape(safeUrl(t.url))}" target="_blank" rel="noopener noreferrer">Primary documentation ↗</a></article>`).join('') : `<div class="empty-filter"><h3>No matching tools</h3><p>Try a broader term or another role.</p></div>`;
}

function renderResources() {
  $('#documents').innerHTML = [{name:'Research specification',description:'The full research brief: eligibility, delivery methods, pipeline requirements, duplicate prevention, and iteration.',path:'documents/research-specification.md'},{name:'Tool-selection report',description:'The recommended core stack, conditional AI modules, primary sources, access terms, and compute limits.',path:'documents/tool-stack.md'}].map(d=>`<article class="document-card"><span class="doc-icon" aria-hidden="true">▧</span><div><h2>${d.name}</h2><p>${d.description}</p><a href="${d.path}" target="_blank" rel="noopener">Read document ↗</a><a href="${d.path}" download>Download ↓</a></div></article>`).join('');
  $('#sources').innerHTML = project.sources.map(s=>`<a class="source-card" href="${escape(safeUrl(s.url))}" target="_blank" rel="noopener noreferrer"><div><strong>${escape(s.name)}</strong><small>${escape(s.description)}</small></div><span aria-hidden="true">↗</span></a>`).join('');
}

function openStream(id) {
  const stream = project.workstreams.find(s=>s.id===id); if(!stream)return;
  $('#dialog-content').innerHTML = `${symbol(stream)}<h2 class="dialog-title" id="dialog-title">${escape(stream.name)}</h2><p>${escape(stream.description)}</p><div class="stream-tags">${stream.tags.map(t=>`<span class="tag">${escape(t)}</span>`).join('')}</div><h3>Questions guiding this workstream</h3><ul>${stream.questions.map(q=>`<li>${escape(q)}</li>`).join('')}</ul><div class="dialog-status"><strong>Planned · evidence review pending</strong><br>No project findings have been published for this workstream. Evidence shared across workstreams will retain one underlying record.</div><div class="dialog-actions"><a class="button primary" href="${escape(safeUrl(stream.sourceUrl))}" target="_blank" rel="noopener noreferrer">${escape(stream.sourceLabel)} ↗</a><button class="small-button" id="dialog-roadmap">View roadmap</button></div>`;
  const dialog = $('#stream-dialog'); dialog.setAttribute('aria-labelledby','dialog-title'); dialog.showModal();
  $('#dialog-roadmap').addEventListener('click',()=>{dialog.close(); location.hash='roadmap';});
}

async function init() {
  try {
    const response = await fetch('data/project.json',{cache:'no-cache'}); if(!response.ok)throw new Error('Snapshot unavailable'); project = await response.json();
    renderOverview(); renderStreams(); renderMilestones(); renderRuns(); renderTools(); renderResources(); showPage();
    $('#updated').textContent = `Updated ${new Intl.DateTimeFormat('en-US',{dateStyle:'long',timeZone:'America/New_York'}).format(new Date(project.updatedDate+'T12:00:00-04:00'))} · ET`;
    document.addEventListener('click',(event)=>{const button=event.target.closest('[data-stream]');if(button)openStream(button.dataset.stream);});
    $('#stream-search').addEventListener('input',renderStreams); $('#family-filter').addEventListener('change',renderStreams);
    $('#tool-search').addEventListener('input',renderTools); $('#tool-tier').addEventListener('change',renderTools);
    $('#run-search').addEventListener('input',renderRuns); $('#evidence-filter').addEventListener('change',renderRuns);
    $('#milestone-filter').addEventListener('click',event=>{const button=event.target.closest('[data-filter]');if(!button)return;milestoneFilter=button.dataset.filter;$$('#milestone-filter button').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));renderMilestones();});
    $('#export').addEventListener('click',()=>{download(`abcd1-project-${project.updatedDate}.json`,JSON.stringify(project,null,2)+'\n','application/json');notify('Project snapshot downloaded.');});
    $('#runs-export').addEventListener('click',()=>{const fields=['id','variant','tool','vectorMethod','endpoint','evidenceType','status','sourceUrl'];const cell=v=>'"'+String(v??'').replaceAll('"','""')+'"';download(`abcd1-published-runs-${project.updatedDate}.csv`,[fields.join(','),...project.runs.map(r=>fields.map(f=>cell(r[f])).join(','))].join('\r\n')+'\r\n','text/csv');notify(project.runs.length?'Published runs downloaded.':'CSV downloaded with column headers; no runs are published.');});
    $('#menu-toggle').addEventListener('click',()=>{const expanded=$('#primary-nav').classList.toggle('open');$('#menu-toggle').setAttribute('aria-expanded',String(expanded));});
    $('.dialog-close').addEventListener('click',()=>$('#stream-dialog').close());
    $('#stream-dialog').addEventListener('click',event=>{if(event.target===$('#stream-dialog')){const r=event.target.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)event.target.close();}});
    window.addEventListener('hashchange',showPage);
  } catch(error) {
    $('#metrics').innerHTML = `<div class="empty-filter"><h3>The project snapshot could not be loaded.</h3><p>Refresh the page, or read the documents through the links below. No research counts are inferred while data is unavailable.</p><a href="documents/research-specification.md" class="text-link">Read the research specification →</a></div>`;
    $('#updated').textContent='Snapshot unavailable';
    $('#export').disabled=true; $('#runs-export').disabled=true;
    $('#export').title='Snapshot unavailable';
    window.addEventListener('hashchange',showPage);showPage();
  }
}
init();
