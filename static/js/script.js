const uploadZone=document.getElementById('uploadZone');
const fileInput=document.getElementById('fileInput');
const previewImg=document.getElementById('previewImg');
const upPrompt=document.getElementById('upPrompt');
const removeBtn=document.getElementById('removeBtn');
const detectBtn=document.getElementById('detectBtn');
const resultCard=document.getElementById('resultCard');
let selectedFile=null;

uploadZone.addEventListener('click',e=>{
  if(!removeBtn.contains(e.target))fileInput.click();
});
['dragover','dragenter'].forEach(ev=>
  uploadZone.addEventListener(ev,e=>{
    e.preventDefault();uploadZone.classList.add('over');
  })
);
['dragleave','dragend'].forEach(ev=>
  uploadZone.addEventListener(ev,()=>uploadZone.classList.remove('over'))
);
uploadZone.addEventListener('drop',e=>{
  e.preventDefault();
  uploadZone.classList.remove('over');
  if(e.dataTransfer.files[0])setFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener('change',e=>{
  if(e.target.files[0])setFile(e.target.files[0]);
});
removeBtn.addEventListener('click',e=>{
  e.stopPropagation();
  selectedFile=null;fileInput.value='';
  previewImg.style.display='none';
  removeBtn.style.display='none';
  upPrompt.style.display='flex';
  detectBtn.disabled=true;
  resultCard.style.display='none';
});

function setFile(f){
  if(!f.type.startsWith('image/')){
    toast('Please select a valid image file','e');return;
  }
  selectedFile=f;
  const r=new FileReader();
  r.onload=e=>{
    previewImg.src=e.target.result;
    previewImg.style.display='block';
    upPrompt.style.display='none';
    removeBtn.style.display='flex';
    detectBtn.disabled=false;
  };
  r.readAsDataURL(f);
}

async function analyze(){
  if(!selectedFile)return;
  detectBtn.disabled=true;
  detectBtn.innerHTML='<span class="loader"><span></span><span></span><span></span></span> ANALYZING...';
  try{
    const fd=new FormData();
    fd.append('fingerprint',selectedFile);
    const res=await fetch('/predict',{method:'POST',body:fd});
    const data=await res.json();
    if(data.success){showResult(data);toast('✅ Blood group detected!','s');}
    else toast(data.error||'Detection failed','e');
  }catch(e){
    toast('Request failed. Try again.','e');
  }finally{
    detectBtn.disabled=false;
    detectBtn.innerHTML='🔍 DETECT BLOOD GROUP';
  }
}

function showResult(data){
  resultCard.style.display='block';
  resultCard.scrollIntoView({behavior:'smooth',block:'nearest'});
  const bg=document.getElementById('resultBG');
  bg.style.opacity='0';bg.style.transform='scale(0.3)';
  setTimeout(()=>{
    bg.textContent=data.blood_group;
    bg.style.transition='all 0.6s cubic-bezier(0.175,0.885,0.32,1.275)';
    bg.style.opacity='1';bg.style.transform='scale(1)';
  },80);
  const cn=document.getElementById('confNum');
  cn.textContent=data.confidence.toFixed(1)+'%';
  cn.className='conf-num '+(data.confidence>=80?'high':data.confidence>=60?'mid':'low');
  document.getElementById('patternType').textContent=data.features.pattern_type;
  document.getElementById('ridgeCount').textContent=data.features.ridge_count.toLocaleString();
  document.getElementById('minutiaeCount').textContent=data.features.minutiae_count;
  const chart=document.getElementById('probChart');
  chart.innerHTML='';
  Object.entries(data.probabilities)
    .sort((a,b)=>b[1]-a[1])
    .forEach(([bg,pct])=>{
      const row=document.createElement('div');
      row.className='prob-row';
      row.innerHTML=`
        <span class="prob-lbl">${bg}</span>
        <div class="prob-track">
          <div class="prob-fill" style="width:0" data-w="${pct}%"></div>
        </div>
        <span class="prob-val">${pct.toFixed(1)}%</span>`;
      chart.appendChild(row);
    });
  requestAnimationFrame(()=>{
    setTimeout(()=>{
      chart.querySelectorAll('.prob-fill').forEach(b=>{
        b.style.width=b.dataset.w;
      });
    },120);
  });
}

window.addEventListener('load',()=>{
  document.querySelectorAll('.bar-fill').forEach(b=>{
    const w=b.dataset.w;
    b.style.width='0';
    setTimeout(()=>{b.style.width=w;},400);
  });
});

function toast(msg,type='s'){
  const el=document.createElement('div');
  el.className=`toast ${type}`;
  el.textContent=msg;
  document.body.appendChild(el);
  setTimeout(()=>{
    el.style.animation='tout 0.3s ease-in forwards';
    setTimeout(()=>{el.parentNode&&el.parentNode.removeChild(el);},320);
  },3000);
}
