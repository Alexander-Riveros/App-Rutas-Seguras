async function cargarDatos() {
  const res = await fetch('/leer');                  // Llama al endpoint Flask para obtener los datos
  const datos = await res.json();                    // Convierte la respuesta JSON a objeto JS
  const lista = document.getElementById('lista');    // Obtiene el contenedor donde se mostrarán los datos
  lista.innerHTML = '';                              // Limpia la lista antes de mostrar datos nuevos

  for (let id in datos) {                            // Recorre cada elemento del objeto (clave = ID de Firebase)
    const item = document.createElement('ion-item'); // Crea un componente de lista (IONIC)
    item.innerHTML = `
      ${datos[id].texto}
      <ion-button color="danger" size="small" onclick="eliminarDato('${id}')">
        <ion-icon name="trash-outline"></ion-icon>
      </ion-button>
    `;
    lista.appendChild(item);                         // Agrega cada item a la lista
  }
}


async function crearDato() {
  const input = document.getElementById('dato');     // Obtiene el campo de entrada
  const texto = input.value;                         // Obtiene el texto ingresado
  if (texto.trim() === '') return;                   // No hace nada si está vacío

  await fetch('/crear', {                            // Llama al endpoint Flask para crear un nuevo ítem
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({texto})                    // Envía el texto como JSON al servidor
  });

  input.value = '';                                   // Limpia el input
  cargarDatos();                                      // Recarga la lista con el nuevo dato
}


async function eliminarDato(id) {
  await fetch(`/eliminar/${id}`, {
    method: 'DELETE'                                 // Llama al endpoint Flask para eliminar el ítem
  });
  cargarDatos();                                     // Recarga la lista para reflejar el cambio
}


window.onload = cargarDatos;
