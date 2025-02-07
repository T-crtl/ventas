// Función para guardar las cantidades de todos los productos
function guardarCantidades(idsProductos) {
    const cantidades = {};
    idsProductos.forEach(productoId => {
        const input = document.querySelector(`input[name="cantidad_${productoId}"]`);
        if (input) {
            cantidades[productoId] = input.value; // Guardar la cantidad
            console.log(`Guardando cantidad para producto ${productoId}: ${input.value}`); // Depuración
        }
    });
    return cantidades;
}

// Función para restaurar las cantidades guardadas
function restaurarCantidades(cantidades) {
    Object.keys(cantidades).forEach(productoId => {
        const input = document.querySelector(`input[name="cantidad_${productoId}"]`);
        if (input) {
            input.value = cantidades[productoId]; // Restaurar la cantidad
            console.log(`Restaurando cantidad para producto ${productoId}: ${cantidades[productoId]}`); // Depuración
        }
    });
}

// Manejar el cambio en el filtro
document.getElementById('linea_producto').addEventListener('change', function () {
    const lineaProducto = this.value;
    console.log(`Línea de producto seleccionada: ${lineaProducto}`); // Depuración

    // Obtener los IDs de todos los productos
    const idsProductos = JSON.parse(document.getElementById('idsProductos').textContent);

    // Guardar las cantidades de todos los productos antes de cambiar el filtro
    const cantidades = guardarCantidades(idsProductos);
    console.log('Cantidades guardadas:', cantidades); // Depuración

    // Enviar la solicitud de filtrado con Fetch
    fetch(`?linea_producto=${lineaProducto}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'  // Para identificar solicitudes AJAX en Django
        }
    })
        .then(response => response.json())
        .then(data => {
            console.log('Respuesta recibida:', data); // Depuración

            // Actualizar solo la sección de productos
            document.getElementById('productosContainer').innerHTML = data.html;

            // Restaurar las cantidades después de cambiar el filtro
            restaurarCantidades(cantidades);
        })
        .catch(error => {
            console.error('Error en la solicitud Fetch:', error); // Depuración
        });
});

// Esperamos a que el documento cargue completamente
document.addEventListener('DOMContentLoaded', function () {
    const clienteSelect = document.getElementById('id_cliente');

    clienteSelect.addEventListener('change', function () {
        const clienteId = clienteSelect.value;
        if (clienteId) {
            fetch(`/modulo_ventas/obtener_datos_cliente/?cliente_id=${clienteId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                    } else {
                        if (document.getElementById('numero_cliente')) {
                            document.getElementById('numero_cliente').value = data.numero_cliente || '';
                        }
                        if (document.getElementById('cliente')) {
                            document.getElementById('cliente').value = data.cliente || '';
                        }
                        if (document.getElementById('calle')) {
                            document.getElementById('calle').value = data.calle || '';
                        }
                        if (document.getElementById('colonia')) {
                            document.getElementById('colonia').value = data.colonia || 'No especificada';
                        }
                        if (document.getElementById('municipio')) {
                            document.getElementById('municipio').value = data.municipio || '';
                        }
                        if (document.getElementById('estado')) {
                            document.getElementById('estado').value = data.estado || '';
                        }
                        if (document.getElementById('codigo')) {
                            document.getElementById('codigo').value = data.codigo || '';
                        }
                        if (document.getElementById('email')) {
                            document.getElementById('email').value = data.email || 'Sin email';
                        }
                        if (document.getElementById('telefono_cliente')) {
                            document.getElementById('telefono_cliente').value = data.telefono_cliente || '';
                        }

                    }
                })
                .catch(error => {
                    console.error('Error al obtener datos del cliente:', error);
                });
        }
    });
});