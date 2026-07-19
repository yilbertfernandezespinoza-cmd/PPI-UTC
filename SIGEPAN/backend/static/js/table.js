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

    }

};