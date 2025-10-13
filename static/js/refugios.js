// JS para el módulo Refugios
// Exporta initRefugios() global para inicializar el módulo tanto en carga directa como cuando se inyecta por AJAX.
(function(){
  // Base URL para las APIs
  const apiBase = '/api/refugios'
  async function cargarRefugios(){
    const grid = document.getElementById('gridRefugios')
    if(!grid) return
    grid.innerHTML = '<div class="col-span-full flex justify-center items-center py-16"><div class="loading-spinner"></div></div>'
    try{
      const res = await fetch('/api/refugios')
      const data = await res.json()
      grid.innerHTML = ''
      if(!Array.isArray(data)){
        grid.innerHTML = '<div class="col-span-full text-center text-red-500 py-12"><i class="fas fa-exclamation-circle text-4xl mb-2"></i><p>Error cargando datos</p></div>'
        return
      }
      if(data.length === 0){
        grid.innerHTML = '<div class="col-span-full text-center text-gray-500 py-12"><i class="fas fa-inbox text-4xl mb-2 opacity-50"></i><p>No hay refugios registrados</p></div>'
        return
      }
      data.forEach(r => grid.appendChild(crearTarjeta(r)))
    }catch(e){
      grid.innerHTML = '<div class="col-span-full text-center text-red-500 py-12"><i class="fas fa-wifi-off text-4xl mb-2"></i><p>Error de conexión</p></div>'
    }
  }

  function crearTarjeta(r){
    const card = document.createElement('div')
    card.className = 'card-hover bg-white rounded-2xl p-6 shadow-md'
    card.innerHTML = `
      <div class="flex items-start justify-between mb-4">
        <div class="flex-1">
          <h3 class="text-xl font-bold text-gray-800 mb-1">${escapeHtml(r.nombre || '')}</h3>
          <p class="text-sm text-gray-600 flex items-center gap-1">
            <i class="fas fa-map-marker-alt text-purple-600"></i>
            ${escapeHtml(r.direccion || 'Dirección no especificada')}
          </p>
        </div>
        <div class="badge-capacity px-3 py-1 rounded-full text-xs font-semibold">
          <i class="fas fa-users mr-1"></i>${r.capacidad ?? '-'}
        </div>
      </div>

      <div class="space-y-3 mb-4 pb-4 border-b border-gray-200">
        <div class="flex items-center gap-2 text-sm text-gray-700">
          <i class="fas fa-envelope text-purple-600 w-4"></i>
          <span>${escapeHtml(r.correoElectronico || 'No especificado')}</span>
        </div>
        <div class="flex items-center gap-2 text-sm text-gray-700">
          <i class="fas fa-phone text-purple-600 w-4"></i>
          <span>${escapeHtml(r.telefono || 'No especificado')}</span>
        </div>
        ${r.fechaFundacion ? `<div class="flex items-center gap-2 text-sm text-gray-700"><i class="fas fa-calendar text-purple-600 w-4"></i><span>${new Date(r.fechaFundacion).toLocaleDateString('es-ES')}</span></div>` : ''}
      </div>

      ${r.descripcion ? `<p class="text-sm text-gray-600 mb-4 italic">"${escapeHtml(r.descripcion)}"</p>` : ''}

      <div class="flex gap-2">
        <button data-id="${r.idRefugio}" class="editar flex-1 btn-secondary py-2 rounded-lg text-sm font-semibold transition flex items-center justify-center gap-2">
          <i class="fas fa-edit"></i> Editar
        </button>
        <button data-id="${r.idRefugio}" class="eliminar flex-1 btn-danger py-2 rounded-lg text-sm font-semibold transition flex items-center justify-center gap-2">
          <i class="fas fa-trash"></i> Eliminar
        </button>
      </div>
    `

    card.querySelector('.editar').addEventListener('click', ()=> openModalEditar(r))
    card.querySelector('.eliminar').addEventListener('click', ()=> eliminarRefugio(r.idRefugio))

    return card
  }

  function escapeHtml(s){ if(!s) return ''; return String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;') }

  function showAlert(msg, type='success'){
    const a = document.getElementById('alert')
    const title = document.getElementById('alertTitle')
    const msgEl = document.getElementById('alertMsg')
    if(!a) return
    a.className = type === 'success' ? 'alert-success' : 'alert-error'
    a.classList.add('fixed','top-6','right-6','max-w-md','rounded-xl','p-4','text-white','shadow-lg','z-40')
    if(title) title.textContent = type === 'success' ? '✓ Éxito' : '⚠ Error'
    if(msgEl) msgEl.textContent = msg
    a.classList.remove('hidden')
    setTimeout(()=> a.classList.add('hidden'), 4000)
  }

  // Modal & form handlers
  function abrirModal(){ const modal = document.getElementById('modal'); if(!modal) { console.warn('refugios: modal element not found'); return; } modal.classList.remove('hidden'); modal.classList.add('flex'); console.log('refugios: modal opened') }
  function cerrarModal(){ const modal = document.getElementById('modal'); const form = document.getElementById('formRefugio'); if(!modal || !form) return; modal.classList.remove('flex'); modal.classList.add('hidden'); form.reset(); const idEl = document.getElementById('idRefugio'); if(idEl) idEl.value = '' }

  function openModalNuevo(){ const title = document.getElementById('modalTitle'); const idEl = document.getElementById('idRefugio'); const form = document.getElementById('formRefugio'); if(title) title.innerText='Nuevo Refugio'; if(idEl) idEl.value=''; if(form) form.reset(); console.log('refugios: openModalNuevo called'); abrirModal() }
  function openModalEditar(r){ const title = document.getElementById('modalTitle'); const idEl = document.getElementById('idRefugio'); if(title) title.innerText='Editar Refugio'; if(idEl) idEl.value = r.idRefugio; const names = ['nombre','direccion','telefono','correoElectronico','capacidad','fechaFundacion','descripcion']; names.forEach(n=>{ const el = document.getElementById(n); if(el) el.value = r[n] || '' }); abrirModal() }

  async function eliminarRefugio(id){
    if(!confirm('¿Eliminar este refugio? Esta acción no se puede deshacer.')) return;
    try{
      const res = await fetch(`${apiBase}/${id}`, { method: 'DELETE' });
      const data = await res.json();
      if(res.status === 409 || (data && data.code === 'fk_dependency')){
        // El servidor indica que existen dependencias relacionadas
        let extra = ''
        if(data && data.dependentCounts){
          const c = data.dependentCounts
          extra = `\n\nResumen: ${c.apoyos ?? 'N/A'} apoyos, ${c.mascotas ?? 'N/A'} mascotas relacionados.`
        }
        const ok = confirm((data && data.message ? data.message : 'Existen elementos relacionados.') + extra + "\n\nSi confirmas, se eliminarán también los registros relacionados. ¿Deseas continuar?")
        if(ok){
          // Llamar endpoint explícito de eliminación en cascada
          try{
            const res2 = await fetch(`/api/refugios/${id}/force_delete`, { method: 'POST' })
            const data2 = await res2.json()
            if(data2.success){ showAlert(data2.message || 'Refugio y apoyos eliminados'); cargarRefugios(); }
            else{ showAlert(data2.message || 'Error al eliminar con fuerza','error') }
          }catch(err){ console.error('Error force delete', err); showAlert('Error de conexión al eliminar con fuerza','error') }
        } else {
          showAlert('Operación cancelada', 'error')
        }
      } else if(data.success) {
        showAlert(data.message || 'Refugio eliminado')
        cargarRefugios()
      } else {
        showAlert(data.message || 'Error al eliminar','error')
      }
    }catch(e){
      console.error('Error eliminarRefugio', e)
      showAlert('Error de conexión','error')
    }
  }

  // form submit
  async function onSubmitHandler(ev){ ev.preventDefault(); const id = document.getElementById('idRefugio')?.value; const payload = { nombre: document.getElementById('nombre')?.value, direccion: document.getElementById('direccion')?.value, telefono: document.getElementById('telefono')?.value, correoElectronico: document.getElementById('correoElectronico')?.value, capacidad: document.getElementById('capacidad')?.value ? Number(document.getElementById('capacidad').value) : null, fechaFundacion: document.getElementById('fechaFundacion')?.value || null, descripcion: document.getElementById('descripcion')?.value }
    try{
      let res
      if(id){ res = await fetch(`${apiBase}/${id}`, { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) }) }
      else{ res = await fetch(apiBase, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) }) }
      const data = await res.json()
      if(data.success){ showAlert(data.message || 'Guardado correctamente'); cerrarModal(); cargarRefugios() } else { showAlert(data.message || 'Error al guardar','error') }
    }catch(e){ showAlert('Error de conexión','error') }
  }

  // inicializador — idempotente
  function initRefugios(){
    // conectar botones si existen
    const btnNuevo = document.getElementById('btnNuevo')
    if(btnNuevo && !btnNuevo.__refugios_bound){ btnNuevo.addEventListener('click', openModalNuevo); btnNuevo.__refugios_bound = true; console.log('refugios: btnNuevo bound') }
    const closeModal = document.getElementById('closeModal')
    if(closeModal && !closeModal.__refugios_bound){ closeModal.addEventListener('click', cerrarModal); closeModal.__refugios_bound = true }
    const btnCancelar = document.getElementById('btnCancelar')
    if(btnCancelar && !btnCancelar.__refugios_bound){ btnCancelar.addEventListener('click', cerrarModal); btnCancelar.__refugios_bound = true }
    const form = document.getElementById('formRefugio')
    if(form && !form.__refugios_bound){ form.addEventListener('submit', onSubmitHandler); form.__refugios_bound = true }
    // cargar datos
    console.log('refugios: initRefugios running')
    cargarRefugios()
  }

  // Exponer globalmente
  window.initRefugios = initRefugios
})()
