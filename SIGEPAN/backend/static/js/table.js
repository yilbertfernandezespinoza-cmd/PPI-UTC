window.SIGEPAN = window.SIGEPAN || {};

SIGEPAN.table = {

    defaults: {

        layout: "fitColumns",

        pagination: true,

        paginationSize: 10,

        paginationSizeSelector: [10,25,50,100],

        movableColumns: false,

        resizableRows: false,

        placeholder: "No hay registros disponibles",

        locale: "es-es",

        langs:{
            "es-es":{
                pagination:{
                    page_size:"Registros",
                    page_title:"Mostrar página",
                    first:"Primera",
                    first_title:"Primera página",
                    last:"Última",
                    last_title:"Última página",
                    prev:"Anterior",
                    prev_title:"Página anterior",
                    next:"Siguiente",
                    next_title:"Página siguiente",
                    all:"Todos"
                }
            }
        }

    },

    create(config){

        const {

            selector,

            search = null,

            ...options

        } = config;

        const tabla = new Tabulator(selector,{

            ...this.defaults,

            ...options

        });

        if(search){

            const input = document.querySelector(search);

            if(input){

                input.addEventListener("input",function(){

                    const valor = this.value
                        .toLowerCase()
                        .trim();

                    if(!valor){

                        tabla.clearFilter();

                        return;

                    }

                    tabla.setFilter(function(data){

                        return Object.values(data).some(campo=>{

                            return String(campo)
                                .toLowerCase()
                                .includes(valor);

                        });

                    });

                });

            }

        }

        return tabla;

    },

    postAction({
        url,
        csrfToken,
        message = "¿Está seguro de realizar esta acción?"
    }) {

        if (!confirm(message)) {
            return;
        }

        fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(response => {

            if (!response.ok) {
                throw new Error("Error al procesar la solicitud.");
            }

            location.reload();

        })
        .catch(error => {

            alert(error.message);

        });

    },

    actions(config) {

        return function (cell) {

            const data = cell.getRow().getData();

            let html = '<div class="d-flex gap-1 justify-content-center">';

            if (config.editField && data[config.editField]) {

                html += `
                    <a
                        href="${data[config.editField]}"
                        class="btn btn-warning btn-sm"
                    >
                        Editar
                    </a>
                `;

            }

            if (
                config.disableField &&
                data[config.disableField] &&
                data.estado
            ) {

                html += `
                    <button
                        class="btn btn-danger btn-sm btn-deshabilitar"
                    >
                        Deshabilitar
                    </button>
                `;

            }

            html += '</div>';

            return html;


        };

    }

};